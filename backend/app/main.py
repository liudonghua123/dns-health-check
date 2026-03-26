from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.api.api_v1.api import api_router
from app.db.session import init_db, get_db
from app.core.config import settings, load_configs_to_cache
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    await init_db()

    # Load configs into cache
    async for db in get_db():
        count = await load_configs_to_cache(db)
        print(f"Loaded {count} configs into cache")
        break

    yield
    # Shutdown: cleanup


app = FastAPI(
    title="DNS Health Check System",
    description="DNS域名健康检测系统",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

# Serve static files (frontend)
public_path = os.path.join(os.path.dirname(__file__), "public")
if os.path.exists(public_path):
    app.mount("/", StaticFiles(directory=public_path, html=True), name="public")
    logger.info(f"Serving static files from: {public_path}")
else:
    logger.warning(f"Public directory not found: {public_path}")


@app.get("/")
async def root():
    return {"message": "DNS Health Check System API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time

    def open_browser():
        time.sleep(1)  # Wait for server to start
        url = f"http://{settings.host}:{settings.port}"
        webbrowser.open(url)

    # Open browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )