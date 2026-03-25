# DNS Health Check System

A DNS domain health detection system that can detect domain status through ping, curl, playwright screenshot, and AI analysis.

## Features

- **Data Sync**: Synchronize shared zones and DNS records from ZDNS API
- **Health Detection**: Support Ping, Curl, Playwright Screenshot, AI Analysis
- **RBAC**: Complete user role permission management
- **Audit Logging**: Complete operation log recording

## Tech Stack

- **Backend**: FastAPI + async SQLAlchemy + JWT
- **Frontend**: Vue 3 + Tailwind CSS + Pinia
- **Database**: SQLite (default, can switch to MySQL/PostgreSQL)

## Quick Start

### Backend

```bash
cd backend

# Create virtual environment and install dependencies
uv sync

# Copy environment configuration
copy .env.example .env
# Edit .env file, configure ZDNS API and OpenAI parameters

# Create admin account
uv run python create_admin.py

# Start the server
uv run python main.py
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Default Account

- Username: admin
- Password: admin123

## Environment Variables

### Backend (.env)

```env
# ZDNS API Configuration
ZDNS_BASE_URL=https://10.10.250.3:20120/
ZDNS_USERNAME=admin
ZDNS_PASSWORD=your_password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# JWT Configuration
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite+aiosqlite:///./dns_health_check.db
```

## API Endpoints

- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/users/` - User list
- `POST /api/v1/sync/zones` - Sync shared zones
- `POST /api/v1/sync/records/{zone_id}` - Sync zone records
- `POST /api/v1/sync/all` - Sync all data
- `POST /api/v1/detect/record/{record_id}` - Detect single record
- `POST /api/v1/detect/zone/{zone_id}` - Detect entire zone
- `POST /api/v1/detect/all` - Detect all records
- `GET /api/v1/records/` - DNS record list (supports search/filter)
- `GET /api/v1/zones/` - Domain zone list
- `GET /api/v1/logs/` - System logs

## Detection Rules

| Record Type | Detection Method |
|-------------|------------------|
| A | ping IP + curl domain + playwright screenshot + AI analysis |
| CNAME | Resolve to target domain, then execute A record detection |
| MX | Check mail server port (25) |
| NS | Check if NS server can resolve |

## License

MIT

## Build Executable (PyInstaller)

### Prerequisites

Install PyInstaller:

```bash
pip install pyinstaller
```

### Build Command

Run from the backend directory:

```bash
cd backend

# Install dependencies first
uv sync

# Build executable
pyinstaller app/main.py --onefile --name dns-health-check.exe --add-data "app;app" --add-data "app/public;public" --hidden-import fastapi --hidden-import uvicorn --hidden-import uvicorn.logging --hidden-import uvicorn.loops --hidden-import uvicorn.loops.auto --hidden-import uvicorn.protocols --hidden-import uvicorn.protocols.http --hidden-import uvicorn.protocols.http.h11 --hidden-import uvicorn.protocols.websockets --hidden-import uvicorn.protocols.websockets.auto --hidden-import uvicorn.lifespan --hidden-import uvicorn.lifespan.on --hidden-import starlette --hidden-import starlette.responses --hidden-import starlette.routing --hidden-import starlette.middleware --hidden-import starlette.middleware.cors --hidden-import starlette.staticfiles --hidden-import sqlalchemy --hidden-import sqlalchemy.ext --hidden-import sqlalchemy.ext.asyncio --hidden-import aiosqlite --hidden-import aiomysql --hidden-import asyncpg --hidden-import bcrypt --hidden-import passlib --hidden-import passlib.handlers --hidden-import passlib.handlers.bcrypt --hidden-import pydantic --hidden-import pydantic_settings --hidden-import jose --hidden-import jose.jwt --hidden-import jose.utils --hidden-import jose.backends --hidden-import jose.backends.cryptography_backend --hidden-import cryptography --hidden-import python_multipart --hidden-import docx --hidden-import reportlab --hidden-import passlib.context --paths ".venv/Lib/site-packages"

### Build Output

The executable will be created at `backend/dist/dns-health-check.exe`.

### Run the Executable

```bash
# The executable will serve both frontend and backend
# Default port: 9000 (configurable in .env)

./dist/dns-health-check.exe
```

### Note

- The frontend static files in `app/public/` are bundled into the executable
- Run `npm run build` in the frontend directory first, then rebuild the PyInstaller package
- SQLite database will be created in the executable's directory