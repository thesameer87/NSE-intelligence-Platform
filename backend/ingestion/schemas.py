from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RawSmartAPIResponse(BaseModel):
    """
    Standard SmartAPI response envelope.
    """

    status: bool
    message: str
    errorcode: str
    data: dict[str, Any] | list[Any] | None = None

    model_config = ConfigDict(strict=True)


class NormalizedTick(BaseModel):
    """
    Unified internal format for a single market tick.
    """

    symbol: str
    timestamp: datetime
    last_price: float = Field(gt=0)
    volume: Optional[int] = Field(default=None, ge=0)

    model_config = ConfigDict(strict=True)
