from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, sync, detect, records, logs, config

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(sync.router)
api_router.include_router(detect.router)
api_router.include_router(records.router)
api_router.include_router(records.zones_router)
api_router.include_router(logs.router)
api_router.include_router(config.router)