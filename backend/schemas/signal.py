from uuid import UUID

from pydantic import Field

from backend.schemas.common import BaseSchema, TimeStampedSchema


class TradingSignalBase(BaseSchema):
    """Base schema for trading signals."""

    symbol: str = Field(..., description="NSE Stock Symbol")
    signal: str = Field(..., description="Bullish, Bearish, or Neutral")
    confidence: float = Field(..., ge=0.0, le=1.0)
    target_price: float
    prediction_source: str
    outcome: str | None = None


class TradingSignalCreate(TradingSignalBase):
    """Schema for creating a trading signal."""

    pass


class TradingSignalResponse(TradingSignalBase, TimeStampedSchema):
    """Schema for returning a trading signal."""

    id: UUID
