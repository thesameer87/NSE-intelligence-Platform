from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.market_tick import IntradayTick, DailyOHLCV
from backend.ingestion.schemas import NormalizedTick
from backend.schemas.market import DailyOHLCVResponse, IntradayTickResponse
from backend.persistence.exceptions import DatabaseOperationError
from backend.persistence.interfaces import IMarketDataRepository
from backend.utils.logger import logger


class MarketDataRepository(IMarketDataRepository):
    """
    Concrete implementation of market data persistence using SQLAlchemy async session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_tick(self, tick: NormalizedTick) -> None:
        """
        Persist a NormalizedTick to the IntradayTick ORM model.
        """
        try:
            db_tick = IntradayTick(
                symbol=tick.symbol,
                timestamp=tick.timestamp,
                ltp=tick.last_price,
                # L2 data is explicitly omitted rather than mutated to 0.0
                bid_price=None,
                ask_price=None,
                bid_qty=None,
                ask_qty=None,
                # Volume semantics are preserved exactly
                volume=tick.volume,
                cold_storage_uploaded=False,
            )
            self.session.add(db_tick)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to persist tick for {tick.symbol}: {e}")
            raise DatabaseOperationError(f"Database error while saving tick: {e}")

    async def get_latest_tick(self, symbol: str) -> Optional[NormalizedTick]:
        """
        Retrieve the latest tick from the database and translate it 
        back to NormalizedTick.
        """
        try:
            stmt = (
                select(IntradayTick)
                .where(IntradayTick.symbol == symbol)
                .order_by(IntradayTick.timestamp.desc())
                .limit(1)
            )
            result = await self.session.execute(stmt)
            db_tick = result.scalar_one_or_none()

            if not db_tick:
                return None

            return NormalizedTick(
                symbol=db_tick.symbol,
                timestamp=db_tick.timestamp,
                last_price=db_tick.ltp,
                # Volume semantics strictly preserved
                volume=db_tick.volume,
            )
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch latest tick for {symbol}: {e}")
            raise DatabaseOperationError("Database error while fetching tick") from e

    async def get_intraday_ticks(self, symbol: str) -> list[IntradayTickResponse]:
        """Retrieve recent intraday ticks for a symbol."""
        try:
            stmt = (
                select(IntradayTick)
                .where(IntradayTick.symbol == symbol)
                .order_by(IntradayTick.timestamp.desc())
            )
            result = await self.session.execute(stmt)
            ticks = result.scalars().all()
            
            return [
                IntradayTickResponse(
                    id=t.id,
                    symbol=t.symbol,
                    timestamp=t.timestamp,
                    ltp=t.ltp,
                    bid_price=t.bid_price,
                    ask_price=t.ask_price,
                    bid_qty=t.bid_qty,
                    ask_qty=t.ask_qty,
                    volume=t.volume,
                    cold_storage_uploaded=t.cold_storage_uploaded,
                )
                for t in ticks
            ]
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch ticks for {symbol}: {e}")
            raise DatabaseOperationError("Database error while fetching ticks") from e

    async def get_daily_ohlcv(self, symbol: str) -> list[DailyOHLCVResponse]:
        """Retrieve recent OHLCV bars for a symbol."""
        try:
            stmt = (
                select(DailyOHLCV)
                .where(DailyOHLCV.symbol == symbol)
                .order_by(DailyOHLCV.trade_date.desc())
            )
            result = await self.session.execute(stmt)
            bars = result.scalars().all()
            
            return [
                DailyOHLCVResponse(
                    id=b.id,
                    symbol=b.symbol,
                    trade_date=b.trade_date,
                    open=b.open,
                    high=b.high,
                    low=b.low,
                    close=b.close,
                    volume=b.volume,
                )
                for b in bars
            ]
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch OHLCV for {symbol}: {e}")
            raise DatabaseOperationError("Database error while fetching OHLCV") from e
