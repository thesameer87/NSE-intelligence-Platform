from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from backend.db.models.signal import TradingSignal
from backend.schemas.signal import TradingSignalResponse
from backend.persistence.exceptions import DatabaseOperationError
from backend.utils.logger import logger


class ISignalRepository(Protocol):
    """Protocol for signal persistence operations."""
    async def get_signals(self) -> list[TradingSignalResponse]: ...


class SignalRepository:
    """Concrete implementation of ISignalRepository."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_signals(self) -> list[TradingSignalResponse]:
        """Fetch trading signals."""
        try:
            stmt = select(TradingSignal).order_by(TradingSignal.created_at.desc())
            result = await self.session.execute(stmt)
            signals = result.scalars().all()
            
            return [
                TradingSignalResponse(
                    id=s.id,
                    symbol=s.symbol,
                    signal=s.signal,
                    confidence=s.confidence,
                    target_price=s.target_price,
                    prediction_source=s.prediction_source,
                    outcome=s.outcome,
                    created_at=s.created_at,
                )
                for s in signals
            ]
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch signals: {e}")
            raise DatabaseOperationError("Database error while fetching signals") from e
