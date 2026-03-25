# FastAPI + Vue 3 Full-Stack Project Skill

## Project Overview

A database security audit system with:
- **Backend**: FastAPI + async SQLAlchemy + JWT + RBAC
- **Frontend**: Vue 3 + Tailwind CSS + Pinia + Vue I18n
- **Multi-database**: SQLite, MySQL, PostgreSQL support
- **Features**: Background scanning, audit logging, report export (PDF/DOCX)

## Tech Stack

### Backend
- Python 3.13+
- FastAPI (async web framework)
- SQLAlchemy 2.0+ (async ORM)
- Pydantic (data validation)
- python-jose (JWT)
- passlib + bcrypt (password hashing)
- aiosqlite, aiomysql, asyncpg (async DB drivers)
- reportlab, python-docx (PDF/DOCX export)

### Frontend
- Vue 3 (Composition API)
- Tailwind CSS
- Pinia (state management)
- Vue Router
- Vue I18n (internationalization)
- Axios (HTTP client)
- vue-toastification (notifications)

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   │   └── api_v1/
│   │   │       └── endpoints/
│   │   ├── core/          # Config, security
│   │   ├── db/            # Models, session
│   │   ├── schemas/       # Pydantic models
│   │   └── services/      # Business logic
│   ├── main.py            # Entry point
│   ├── create_admin.py    # Admin script
│   └── pyproject.toml     # Dependencies
├── frontend/
│   ├── src/
│   │   ├── views/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── stores/        # Pinia stores
│   │   ├── router/        # Vue Router
│   │   └── i18n.js        # Translations
│   └── package.json
└── README.md
```

## Common Tasks

### 1. Add New API Endpoint

```python
# backend/app/api/api_v1/endpoints/new_endpoint.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.db import models

router = APIRouter()

@router.get("/")
async def read_items(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    # Your logic here
    return []
```

Register in `api.py`:
```python
from app.api.api_v1.endpoints import new_endpoint
api_router.include_router(new_endpoint.router, prefix="/new", tags=["new"])
```

### 2. Add New Database Model

```python
# backend/app/db/models.py
class NewModel(Base):
    __tablename__ = "new_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 3. Add Frontend Page

```vue
<!-- frontend/src/views/NewPage.vue -->
<template>
  <div class="page-content">
    <h1>{{ $t('new.title') }}</h1>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const data = ref([])
onMounted(async () => {
  const res = await api.get('/new/')
  data.value = res.data
})
</script>
```

Register in router:
```javascript
// frontend/src/router/index.js
import NewPage from '../views/NewPage.vue'
{ path: 'new', component: NewPage }
```

### 4. Add i18n Translation

```javascript
// frontend/src/i18n.js
// Add in both en-US and zh-CN sections
new: {
  title: 'New Page',
  // Chinese
  title: '新页面',
}
```

### 5. Background Task (FastAPI)

```python
# backend/app/services/scanner.py
from fastapi import BackgroundTasks

async def run_task(task_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_task, task_id)

async def process_task(task_id: int):
    # Long-running task logic
    pass
```

### 6. Audit Logging

```python
# Create log model in models.py
class SystemLog(Base):
    __tablename__ = "system_logs"
    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
    level = Column(String, default="info")
    user_id = Column(Integer, ForeignKey("users.id"))
    details = Column(Text)  # JSON string

# Log actions
from app.services.logger import log_action
await log_action(db, action="user_login", level="info",
    user_id=user.id, message="User logged in")
```

## Development Commands

```bash
# Backend
cd backend
uv sync
uv run python create_admin.py
uv run python main.py  # Dev server with auto-reload + browser open

# Frontend
cd frontend
npm install
npm run dev    # Dev server
npm run build  # Production build

# PyInstaller (use venv!)
cd backend
uv pip install pyinstaller
uv run pyinstaller sensitive-information-audit.exe.spec
```

## Key Patterns

### Async Database Session
```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### JWT Authentication
```python
# Verify token
user = await deps.get_current_user(db=db, token=token)

# Create token
access_token = security.create_access_token(
    user.username, expires_delta=timedelta(minutes=30)
)
```

### RBAC Check
```python
# In deps.py
def get_current_user(...):
    # Check user roles and permissions
    if not auth_store.has_permission(required_permission):
        raise HTTPException(403)
```

### Frontend API Call
```javascript
import api from '@/api'

// GET
const res = await api.get('/endpoint/')

// POST
await api.post('/endpoint/', { data })

// With auth header (automatic via interceptor)
```

### Frontend Polling (with auto-stop)
```javascript
const pollingEnabled = ref(false)
let pollingInterval = null

const startPolling = () => {
  if (pollingInterval) return
  pollingEnabled.value = true
  pollingInterval = setInterval(fetchData, 5000)
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
  pollingEnabled.value = false
}

onMounted(() => fetchData())
onUnmounted(() => stopPolling())
```

## PyInstaller Notes

- **Always use venv pyinstaller**: `uv run pyinstaller`
- Use `.spec` file for complex builds
- Collect submodules: `collect_submodules('fastapi')`
- Key hidden imports: jose, passlib, sqlalchemy.ext.asyncio