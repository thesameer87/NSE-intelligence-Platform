from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from backend.db.models.portfolio import PortfolioHolding
from backend.schemas.portfolio import PortfolioHoldingResponse
from backend.persistence.exceptions import DatabaseOperationError
from backend.utils.logger import logger


class IPortfolioRepository(Protocol):
    """Protocol for portfolio persistence operations."""
    async def get_holdings(self) -> list[PortfolioHoldingResponse]: ...


class PortfolioRepository:
    """Concrete implementation of IPortfolioRepository."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_holdings(self) -> list[PortfolioHoldingResponse]:
        """Fetch portfolio holdings."""
        try:
            stmt = select(PortfolioHolding).order_by(PortfolioHolding.symbol)
            result = await self.session.execute(stmt)
            holdings = result.scalars().all()
            
            return [
                PortfolioHoldingResponse(
                    symbol=h.symbol,
                    quantity=h.quantity,
                    avg_buy_price=h.avg_buy_price,
                    buy_date=h.buy_date,
                    notes=h.notes,
                    created_at=h.created_at,
                )
                for h in holdings
            ]
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch portfolio holdings: {e}")
            raise DatabaseOperationError("Database error while fetching holdings") from e
