from datetime import date

from pydantic import Field

from backend.schemas.common import BaseSchema, TimeStampedSchema


class PortfolioHoldingBase(BaseSchema):
    """Base schema for portfolio holdings."""

    symbol: str = Field(..., description="NSE Stock Symbol")
    quantity: float
    avg_buy_price: float
    buy_date: date
    notes: str | None = None


class PortfolioHoldingCreate(PortfolioHoldingBase):
    """Schema for creating a portfolio holding."""

    pass


class PortfolioHoldingResponse(PortfolioHoldingBase, TimeStampedSchema):
    """Schema for returning a portfolio holding."""

    pass
