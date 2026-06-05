from fastapi import APIRouter

from backend.config import Settings
from backend.schemas.health import HealthResponse, MetricsResponse
from backend.utils.logger import logger

router = APIRouter(tags=["Health"])
settings = Settings()  # type: ignore[call-arg]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Core health check endpoint for deployment probes.
    """
    logger.debug("Health check endpoint accessed", extra={"correlation_id": "probe"})

    return HealthResponse(
        status="healthy",
        service="backend",
        environment=settings.environment,
    )


from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """
    Stub endpoint for future Prometheus metrics exposure.
    """
    logger.debug("Metrics endpoint accessed")
    return MetricsResponse(status="stub", message="Metrics will be exposed here in V1")

@router.get("/metrics/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics() -> PlainTextResponse:
    """
    Returns actual Prometheus text format metrics.
    """
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
