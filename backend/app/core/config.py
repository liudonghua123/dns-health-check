from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # ZDNS API
    zdns_base_url: str = "https://10.10.250.3:20120/"
    zdns_username: str = "admin"
    zdns_password: str = ""

    # OpenAI
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    ai_prompt_template: str = ""
    ai_enabled: bool = True

    # Detection Settings
    default_ping_enabled: bool = True
    default_curl_enabled: bool = True
    default_playwright_enabled: bool = True
    default_ai_check_enabled: bool = True
    detection_timeout: int = 15
    concurrent_detection_limit: int = 10
    save_screenshot_to_file: bool = True
    snapshot_save_path: str = "./snapshots"

    # System Settings
    system_name: str = "DNS 健康检测系统"
    page_title: str = "DNS Health Check"

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    database_url: str = "sqlite+aiosqlite:///./dns_health_check.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


# Cache for runtime config values
_config_cache: dict = {}


def get_config_value(category: str, key: str, default: Optional[str] = None) -> Optional[str]:
    """Get config value from cache or return default"""
    cache_key = f"{category}:{key}"
    if cache_key in _config_cache:
        return _config_cache[cache_key]
    return default


def set_config_value(category: str, key: str, value: str):
    """Set config value in cache"""
    cache_key = f"{category}:{key}"
    _config_cache[cache_key] = value


def clear_config_cache():
    """Clear config cache"""
    _config_cache.clear()


def get_detection_config(key: str, default: str = "true") -> str:
    """Get detection config value"""
    return get_config_value("detection", key, default)


def get_ai_config(key: str, default: str = "") -> str:
    """Get AI config value"""
    return get_config_value("ai", key, default)


def get_system_config(key: str, default: str = "") -> str:
    """Get system config value"""
    return get_config_value("system", key, default)


def get_zdns_config(key: str, default: str = "") -> str:
    """Get ZDNS config value"""
    return get_config_value("zdns", key, default)


async def load_configs_to_cache(db):
    """Load all configs from database into cache, with .env as fallback"""
    from sqlalchemy import select
    from app.db.models import SystemConfig
    from app.core.config import settings as app_settings

    # Map env vars to config keys
    env_to_config = {
        # System
        ("system", "system_name"): app_settings.system_name,
        ("system", "page_title"): app_settings.page_title,
        # AI
        ("ai", "openai_api_key"): app_settings.openai_api_key,
        ("ai", "openai_base_url"): app_settings.openai_base_url,
        ("ai", "openai_model"): app_settings.openai_model,
        ("ai", "ai_prompt_template"): app_settings.ai_prompt_template,
        ("ai", "ai_enabled"): str(app_settings.ai_enabled).lower(),
        # Detection
        ("detection", "default_ping_enabled"): str(app_settings.default_ping_enabled).lower(),
        ("detection", "default_curl_enabled"): str(app_settings.default_curl_enabled).lower(),
        ("detection", "default_playwright_enabled"): str(app_settings.default_playwright_enabled).lower(),
        ("detection", "default_ai_check_enabled"): str(app_settings.default_ai_check_enabled).lower(),
        ("detection", "detection_timeout"): str(app_settings.detection_timeout),
        ("detection", "concurrent_detection_limit"): str(app_settings.concurrent_detection_limit),
        ("detection", "save_screenshot_to_file"): str(app_settings.save_screenshot_to_file).lower(),
        ("detection", "snapshot_save_path"): app_settings.snapshot_save_path,
        # ZDNS
        ("zdns", "zdns_base_url"): app_settings.zdns_base_url,
        ("zdns", "zdns_username"): app_settings.zdns_username,
        ("zdns", "zdns_password"): app_settings.zdns_password,
    }

    # First, populate with .env defaults
    for (category, key), value in env_to_config.items():
        if value:
            set_config_value(category, key, value)

    # Then, override with database values if they exist
    result = await db.execute(select(SystemConfig))
    configs = result.scalars().all()

    for config in configs:
        if config.value:  # Only override if DB has a value
            set_config_value(config.category, config.key, config.value)

    return len(configs)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()