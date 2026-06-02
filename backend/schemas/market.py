from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from backend.schemas.common import BaseSchema


class IntradayTickBase(BaseSchema):
    """Base schema for intraday market ticks."""

    symbol: str = Field(..., description="NSE Stock Symbol")
    timestamp: datetime
    ltp: float
    bid_price: float | None = None
    ask_price: float | None = None
    bid_qty: float | None = None
    ask_qty: float | None = None
    volume: int | None = None
    cold_storage_uploaded: bool = False


class IntradayTickCreate(IntradayTickBase):
    """Schema for creating a new intraday tick."""

    pass


class IntradayTickResponse(IntradayTickBase):
    """Schema for returning an intraday tick."""

    id: UUID


class DailyOHLCVBase(BaseSchema):
    """Base schema for daily OHLCV bars."""

    symbol: str = Field(..., description="NSE Stock Symbol")
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class DailyOHLCVCreate(DailyOHLCVBase):
    """Schema for creating a new daily OHLCV bar."""

    pass


class DailyOHLCVResponse(DailyOHLCVBase):
    """Schema for returning a daily OHLCV bar."""

    id: UUID
