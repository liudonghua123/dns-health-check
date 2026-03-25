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