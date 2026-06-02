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
    intraday: IntradayPrediction
    nextday: NextDayPrediction


class ModelRegistryBase(BaseSchema):
    """Base schema for ML model registry."""

    model_name: str
    version: str
    metrics_json: dict[str, Any]
    schema_version: str


class ModelRegistryCreate(ModelRegistryBase):
    """Schema for registering a new model version."""

    pass


class ModelRegistryResponse(ModelRegistryBase):
    """Schema for returning model registry information."""

    trained_at: datetime
