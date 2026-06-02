from backend.schemas.common import BaseSchema


class HealthResponse(BaseSchema):
    """Schema for health check responses."""

    status: str
    service: str
    environment: str


class MetricsResponse(BaseSchema):
    """Schema for metrics stub response."""

    status: str
    message: str
