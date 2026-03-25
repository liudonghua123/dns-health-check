from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from app.db.session import get_db
from app.db.models import User, SystemConfig
from app.schemas import (
    SystemConfigResponse,
    SystemConfigCreate,
    SystemConfigUpdate,
    ConfigCategoryResponse,
    ConfigBulkUpdateList,
)
from app.api.deps import get_current_user, require_permission
from app.core.config import get_config_value, set_config_value, load_configs_to_cache
from datetime import datetime
import json

router = APIRouter(prefix="/config", tags=["config"])


# Default configuration values
DEFAULT_CONFIGS = [
    # System settings
    {"category": "system", "key": "system_name", "value": "DNS 健康检测系统", "value_type": "string", "description": "系统显示名称", "is_visible": True},
    {"category": "system", "key": "system_icon", "value": "", "value_type": "string", "description": "系统图标(URL或base64)", "is_visible": True},
    {"category": "system", "key": "page_title", "value": "DNS Health Check", "value_type": "string", "description": "浏览器页面标题", "is_visible": True},

    # AI settings
    {"category": "ai", "key": "openai_api_key", "value": "", "value_type": "string", "description": "OpenAI API Key", "is_visible": True},
    {"category": "ai", "key": "openai_base_url", "value": "https://new-api.app.ynu.edu.cn/v1", "value_type": "string", "description": "OpenAI API 地址", "is_visible": True},
    {"category": "ai", "key": "openai_model", "value": "gpt-4o-mini", "value_type": "string", "description": "OpenAI 模型名称", "is_visible": True},
    {"category": "ai", "key": "ai_prompt_template", "value": "Analyze this screenshot of {url} and determine if the page is normal (accessible and showing expected content) or abnormal (error page, 404, 500, SSL error, etc.). Return JSON: {\"status\": \"normal\" or \"abnormal\", \"reason\": \"brief explanation\"}", "value_type": "string", "description": "AI分析提示词模板", "is_visible": True},
    {"category": "ai", "key": "ai_enabled", "value": "true", "value_type": "bool", "description": "启用AI检测", "is_visible": True},

    # Detection settings
    {"category": "detection", "key": "default_ping_enabled", "value": "true", "value_type": "bool", "description": "默认启用Ping检测", "is_visible": True},
    {"category": "detection", "key": "default_curl_enabled", "value": "true", "value_type": "bool", "description": "默认启用HTTP检测", "is_visible": True},
    {"category": "detection", "key": "default_playwright_enabled", "value": "true", "value_type": "bool", "description": "默认启用截图检测", "is_visible": True},
    {"category": "detection", "key": "default_ai_check_enabled", "value": "true", "value_type": "bool", "description": "默认启用AI分析", "is_visible": True},
    {"category": "detection", "key": "detection_timeout", "value": "15", "value_type": "int", "description": "检测超时时间(秒)", "is_visible": True},
    {"category": "detection", "key": "concurrent_detection_limit", "value": "10", "value_type": "int", "description": "最大并发检测数", "is_visible": True},
    {"category": "detection", "key": "save_screenshot_to_file", "value": "true", "value_type": "bool", "description": "保存截图到文件系统", "is_visible": True},
    {"category": "detection", "key": "snapshot_save_path", "value": "./snapshots", "value_type": "string", "description": "截图保存路径", "is_visible": True},

    # ZDNS settings
    {"category": "zdns", "key": "zdns_base_url", "value": "https://10.10.250.3:20120/", "value_type": "string", "description": "ZDNS API 地址", "is_visible": True},
    {"category": "zdns", "key": "zdns_username", "value": "admin", "value_type": "string", "description": "ZDNS 用户名", "is_visible": True},
    {"category": "zdns", "key": "zdns_password", "value": "", "value_type": "string", "description": "ZDNS 密码", "is_visible": True},
]


async def ensure_default_configs(db: AsyncSession):
    """Ensure default configs exist in database"""
    from app.core.config import settings as app_settings

    result = await db.execute(select(SystemConfig))
    existing = result.scalars().all()

    if not existing:
        # Map .env values to configs
        env_values = {
            ("system", "system_name"): app_settings.system_name,
            ("system", "page_title"): app_settings.page_title,
            ("ai", "openai_api_key"): app_settings.openai_api_key,
            ("ai", "openai_base_url"): app_settings.openai_base_url,
            ("ai", "openai_model"): app_settings.openai_model,
            ("ai", "ai_prompt_template"): app_settings.ai_prompt_template,
            ("ai", "ai_enabled"): str(app_settings.ai_enabled).lower(),
            ("detection", "default_ping_enabled"): str(app_settings.default_ping_enabled).lower(),
            ("detection", "default_curl_enabled"): str(app_settings.default_curl_enabled).lower(),
            ("detection", "default_playwright_enabled"): str(app_settings.default_playwright_enabled).lower(),
            ("detection", "default_ai_check_enabled"): str(app_settings.default_ai_check_enabled).lower(),
            ("detection", "detection_timeout"): str(app_settings.detection_timeout),
            ("detection", "concurrent_detection_limit"): str(app_settings.concurrent_detection_limit),
            ("detection", "save_screenshot_to_file"): str(app_settings.save_screenshot_to_file).lower() if hasattr(app_settings, 'save_screenshot_to_file') else "true",
            ("detection", "snapshot_save_path"): app_settings.snapshot_save_path if hasattr(app_settings, 'snapshot_save_path') else "./snapshots",
            ("zdns", "zdns_base_url"): app_settings.zdns_base_url,
            ("zdns", "zdns_username"): app_settings.zdns_username,
            ("zdns", "zdns_password"): app_settings.zdns_password,
        }

        for config in DEFAULT_CONFIGS:
            # Use .env value if available, otherwise use default
            key = (config["category"], config["key"])
            if key in env_values and env_values[key]:
                config["value"] = env_values[key]

            db_config = SystemConfig(**config)
            db.add(db_config)
        await db.commit()


async def get_config_value(db: AsyncSession, category: str, key: str) -> Optional[str]:
    """Get config value by category and key"""
    result = await db.execute(
        select(SystemConfig).where(
            SystemConfig.category == category,
            SystemConfig.key == key
        )
    )
    config = result.scalar_one_or_none()
    return config.value if config else None


@router.get("/", response_model=List[ConfigCategoryResponse])
async def list_configs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all configs grouped by category"""
    await ensure_default_configs(db)

    result = await db.execute(select(SystemConfig).order_by(SystemConfig.category, SystemConfig.key))
    configs = result.scalars().all()

    # Group by category
    categories = {}
    for config in configs:
        if config.category not in categories:
            categories[config.category] = []
        categories[config.category].append(config)

    return [
        ConfigCategoryResponse(
            category=cat,
            configs=[SystemConfigResponse.model_validate(c) for c in configs_list]
        )
        for cat, configs_list in categories.items()
    ]


@router.get("/categories", response_model=List[str])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all config categories"""
    result = await db.execute(select(SystemConfig.category).distinct())
    categories = result.scalars().all()
    return list(categories)


@router.get("/{category}", response_model=ConfigCategoryResponse)
async def list_configs_by_category(
    category: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List configs by category"""
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.category == category).order_by(SystemConfig.key)
    )
    configs = result.scalars().all()

    if not configs:
        raise HTTPException(status_code=404, detail="Category not found")

    return ConfigCategoryResponse(
        category=category,
        configs=[SystemConfigResponse.model_validate(c) for c in configs]
    )


@router.get("/{category}/{key}", response_model=SystemConfigResponse)
async def get_config(
    category: str,
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single config"""
    result = await db.execute(
        select(SystemConfig).where(
            SystemConfig.category == category,
            SystemConfig.key == key
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    return SystemConfigResponse.model_validate(config)


@router.post("/", response_model=SystemConfigResponse)
async def create_config(
    config: SystemConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config:write")),
):
    """Create a new config"""
    # Check if exists
    result = await db.execute(
        select(SystemConfig).where(
            SystemConfig.category == config.category,
            SystemConfig.key == config.key
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Config already exists")

    db_config = SystemConfig(**config.model_dump())
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)

    # Update cache
    set_config_value(db_config.category, db_config.key, db_config.value or "")

    return SystemConfigResponse.model_validate(db_config)


@router.put("/{category}/{key}", response_model=SystemConfigResponse)
async def update_config(
    category: str,
    key: str,
    config_update: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config:write")),
):
    """Update a config"""
    result = await db.execute(
        select(SystemConfig).where(
            SystemConfig.category == category,
            SystemConfig.key == key
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    # Update fields
    update_data = config_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    config.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(config)

    # Update cache
    set_config_value(config.category, config.key, config.value or "")
    print(f"[CONFIG] Updated: {config.category}:{config.key} = {config.value}")

    return SystemConfigResponse.model_validate(config)


@router.delete("/{category}/{key}")
async def delete_config(
    category: str,
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config:write")),
):
    """Delete a config"""
    result = await db.execute(
        select(SystemConfig).where(
            SystemConfig.category == category,
            SystemConfig.key == key
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    await db.delete(config)
    await db.commit()

    return {"message": "Config deleted"}


@router.post("/bulk")
async def bulk_update_configs(
    bulk_update: ConfigBulkUpdateList,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config:write")),
):
    """Bulk update configs"""
    updated = []
    for config_update in bulk_update.configs:
        result = await db.execute(
            select(SystemConfig).where(
                SystemConfig.category == config_update.category,
                SystemConfig.key == config_update.key
            )
        )
        config = result.scalar_one_or_none()

        if config:
            update_data = config_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field not in ('category', 'key'):
                    setattr(config, field, value)
            config.updated_at = datetime.utcnow()
            updated.append(SystemConfigResponse.model_validate(config))

    await db.commit()

    # Update cache for each updated config
    for config_response in updated:
        set_config_value(config_response.category, config_response.key, config_response.value or "")
        print(f"[CONFIG] Bulk updated: {config_response.category}:{config_response.key} = {config_response.value}")

    return {"message": f"Updated {len(updated)} configs", "configs": updated}


@router.post("/reset")
async def reset_configs(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("config:write")),
):
    """Reset configs to defaults"""
    # Delete existing configs in category (or all)
    if category:
        await db.execute(
            delete(SystemConfig).where(SystemConfig.category == category)
        )
    else:
        await db.execute(delete(SystemConfig))

    await db.commit()

    # Re-add defaults
    await ensure_default_configs(db)

    # Reload cache
    await load_configs_to_cache(db)

    return {"message": "Configs reset to defaults"}