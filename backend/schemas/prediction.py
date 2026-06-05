from datetime import datetime
from typing import Any

from pydantic import Field

from backend.schemas.common import BaseSchema


class IntradayPrediction(BaseSchema):
    """Schema for intraday predictions."""

    direction: str = Field(
        ..., description="Direction of prediction: Bullish, Bearish, or Neutral"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    target_price: float


class Corridor(BaseSchema):
    """Schema for next-day price corridor."""

    lower: float
    upper: float


class NextDayPrediction(BaseSchema):
    """Schema for next-day predictions."""

    direction: str = Field(
        ..., description="Direction of prediction: Bullish, Bearish, or Neutral"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    corridor: Corridor


class PredictionResponse(BaseSchema):
    """Aggregated prediction response for a symbol."""

    symbol: str = Field(..., description="NSE Stock Symbol")
    prediction_runtime_enabled: bool = Field(default=True, description="Whether the prediction runtime is active")
    available_models: list[str] = Field(default_factory=list)
    unavailable_models: list[str] = Field(default_factory=list)
    last_reload_time: str | None = None
    last_reload_status: str | None = None
    intraday: IntradayPrediction | None = None
    nextday: NextDayPrediction | None = None


class ModelRegistryBase(BaseSchema):
    """Base schema for ML model registry."""

    model_name: str
    version: str
    artifact_path: str
    active: bool = True


class ModelRegistryCreate(ModelRegistryBase):
    """Schema for registering a new model version."""

    pass


class ModelRegistryResponse(ModelRegistryBase):
    """Schema for returning model registry information."""

    created_at: datetime


class ModelLatestResponse(BaseSchema):
    """Schema for returning latest models along with reload status."""
    
    last_reload_time: str | None
    last_reload_status: str
    last_reload_duration_ms: float
    models: list[ModelRegistryResponse]


class ModelReloadResponse(BaseSchema):
    """Schema for model reload endpoint."""
    
    success: bool
    reload_time_ms: float
    available_models: list[str]
    unavailable_models: list[str]
    last_reload_time: str | None
    last_reload_status: str
