# DNS 健康检测系统

DNS域名健康检测系统，可检测域名的状态（ping、curl、playwright截图+AI判断）。

## 功能特性

- **数据同步**: 从ZDNS API同步共享区域和DNS记录
- **健康检测**: 支持Ping、Curl、Playwright截图、AI判断
- **RBAC权限**: 完整的用户角色权限管理
- **操作日志**: 完整的审计日志记录

## 技术栈

- **后端**: FastAPI + async SQLAlchemy + JWT
- **前端**: Vue 3 + Tailwind CSS + Pinia
- **数据库**: SQLite (默认，可切换MySQL/PostgreSQL)

## 快速开始

### 后端

```bash
cd backend

# 创建虚拟环境并安装依赖
uv sync

# 复制环境变量配置
copy .env.example .env
# 编辑 .env 文件，配置ZDNS API和OpenAI等参数

# 创建管理员账户
uv run python create_admin.py

# 启动服务
uv run python main.py
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 默认账户

- 用户名: admin
- 密码: admin123

## 环境变量

### 后端 (.env)

```env
# ZDNS API配置
ZDNS_BASE_URL=https://10.10.250.3:20120/
ZDNS_USERNAME=admin
ZDNS_PASSWORD=your_password

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# JWT配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./dns_health_check.db
```

## API端点

- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户
- `GET /api/v1/users/` - 用户列表
- `POST /api/v1/sync/zones` - 同步共享区
- `POST /api/v1/sync/records/{zone_id}` - 同步区域记录
- `POST /api/v1/sync/all` - 同步所有数据
- `POST /api/v1/detect/record/{record_id}` - 检测单条记录
- `POST /api/v1/detect/zone/{zone_id}` - 检测整个区域
- `POST /api/v1/detect/all` - 检测所有记录
- `GET /api/v1/records/` - DNS记录列表（支持搜索过滤）
- `GET /api/v1/zones/` - 域名区域列表
- `GET /api/v1/logs/` - 系统日志

## 检测规则

| 记录类型 | 检测方法 |
|---------|---------|
| A | ping IP + curl 域名 + playwright截图 + AI判断 |
| CNAME | 解析到目标域名，再执行A记录检测 |
| MX | 检查邮件服务器端口(25) |
| NS | 检查NS服务器是否可解析 |

## 许可证

MIT

## 构建可执行文件 (PyInstaller)

### 前置条件

安装 PyInstaller:

```bash
pip install pyinstaller
```

### 构建命令

在 backend 目录下运行:

```bash
cd backend

# 先安装依赖
uv sync

# 构建可执行文件
pyinstaller app/main.py --onefile --name dns-health-check.exe --add-data "app;app" --add-data "app/public;public" --hidden-import fastapi --hidden-import uvicorn --hidden-import uvicorn.logging --hidden-import uvicorn.loops --hidden-import uvicorn.loops.auto --hidden-import uvicorn.protocols --hidden-import uvicorn.protocols.http --hidden-import uvicorn.protocols.http.h11 --hidden-import uvicorn.protocols.websockets --hidden-import uvicorn.protocols.websockets.auto --hidden-import uvicorn.lifespan --hidden-import uvicorn.lifespan.on --hidden-import starlette --hidden-import starlette.responses --hidden-import starlette.routing --hidden-import starlette.middleware --hidden-import starlette.middleware.cors --hidden-import starlette.staticfiles --hidden-import sqlalchemy --hidden-import sqlalchemy.ext --hidden-import sqlalchemy.ext.asyncio --hidden-import aiosqlite --hidden-import aiomysql --hidden-import asyncpg --hidden-import bcrypt --hidden-import passlib --hidden-import passlib.handlers --hidden-import passlib.handlers.bcrypt --hidden-import pydantic --hidden-import pydantic_settings --hidden-import jose --hidden-import jose.jwt --hidden-import jose.utils --hidden-import jose.backends --hidden-import jose.backends.cryptography_backend --hidden-import cryptography --hidden-import python_multipart --hidden-import docx --hidden-import reportlab --hidden-import passlib.context --paths ".venv/Lib/site-packages"

### 构建输出

可执行文件将生成在 `backend/dist/dns-health-check.exe`。

### 运行可执行文件

```bash
# 可执行文件将同时提供前端和后端服务
# 默认端口: 9000 (可在 .env 中配置)

./dist/dns-health-check.exe
```

### 注意

- 前端静态文件 `app/public/` 会打包到可执行文件中
- 构建前需要先在 frontend 目录运行 `npm run build`，然后重新构建 PyInstaller 包
- SQLite 数据库会在可执行文件所在目录创建