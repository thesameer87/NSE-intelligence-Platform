from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from backend.api.health import router as health_router
from backend.api.router import api_router
from backend.config_validator import validate_configuration
from backend.orchestrator.interfaces import ISchedulerTask
from backend.orchestrator.scheduler import MarketScheduler
from backend.websocket.manager import ConnectionManager
from backend.utils.logger import logger
from backend.websocket.router import router as websocket_router

# Validate configuration on import/startup to fail fast
settings = validate_configuration()

# Initialize orchestrator components
orchestrator_tasks: list[ISchedulerTask] = []
scheduler = MarketScheduler(
    interval_seconds=settings.scheduler_interval_seconds, tasks=orchestrator_tasks
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application starting up...")
    app.state.websocket_manager = ConnectionManager()
    await scheduler.start()
    yield
    logger.info("Application shutting down...")
    await scheduler.stop()


app = FastAPI(
    title="NSE Intelligence Platform",
    version="2.0.0",
    description="Production Grade AI Intelligence Architecture API",
    lifespan=lifespan,
)

# Include routers
app.include_router(health_router)
app.include_router(api_router)
app.include_router(websocket_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "NSE Intelligence Platform API is running",
        "environment": settings.environment,
    }
