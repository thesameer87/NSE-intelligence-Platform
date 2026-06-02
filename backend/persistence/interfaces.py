from typing import Optional, Protocol

from backend.ingestion.schemas import NormalizedTick
from backend.schemas.market import DailyOHLCVResponse, IntradayTickResponse


class IMarketDataRepository(Protocol):
    """
    Contract for persisting and retrieving market data.
    Provides a strictly typed, mock-safe boundary.
    """

    async def save_tick(self, tick: NormalizedTick) -> None:
        """Persist a normalized tick to the database."""
        ...

    async def get_latest_tick(self, symbol: str) -> Optional[NormalizedTick]:
        """Retrieve the most recent normalized tick for a given symbol."""
        ...

    async def get_intraday_ticks(self, symbol: str) -> list[IntradayTickResponse]:
        """Retrieve recent intraday ticks for a symbol."""
        ...

    async def get_daily_ohlcv(self, symbol: str) -> list[DailyOHLCVResponse]:
        """Retrieve recent OHLCV bars for a symbol."""
        ...
