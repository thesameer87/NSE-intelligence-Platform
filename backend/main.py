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

from backend.utils.sentry import setup_sentry

# Validate configuration on import/startup to fail fast
settings = validate_configuration()
setup_sentry(settings)

# Initialize orchestrator components
orchestrator_tasks: list[ISchedulerTask] = []
scheduler = MarketScheduler(
    interval_seconds=settings.scheduler_interval_seconds, tasks=orchestrator_tasks
)


from backend.orchestrator.tasks import MockIngestionTask
from backend.db.session import async_session_maker

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application starting up...")
    app.state.websocket_manager = ConnectionManager()
    
    # Use mock credentials before deployment
    if settings.environment in ("development", "test") or settings.angel_one_api_key == "your_api_key_here":
        mock_task = MockIngestionTask(app.state.websocket_manager, async_session_maker)
        orchestrator_tasks.append(mock_task)
        
    await scheduler.start()
    yield
    logger.info("Application shutting down...")
    await scheduler.stop()


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NSE Intelligence Platform",
    version="2.0.0",
    description="Production Grade AI Intelligence Architecture API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",
        "https://nse-intelligence-platform.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
from backend.utils.metrics import http_requests_total

@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    return response

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
