from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dependencies import get_db_session
from backend.persistence.exceptions import DatabaseOperationError
from backend.persistence.market import MarketDataRepository
from backend.schemas.market import DailyOHLCVResponse, IntradayTickResponse
from backend.utils.logger import logger

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/ticks/{symbol}", response_model=list[IntradayTickResponse])
async def get_intraday_ticks(
    symbol: str, session: AsyncSession = Depends(get_db_session)
) -> list[IntradayTickResponse]:
    """Retrieve intraday market ticks."""
    try:
        repo = MarketDataRepository(session)
        return await repo.get_intraday_ticks(symbol)
    except DatabaseOperationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


@router.get("/ohlcv/{symbol}", response_model=list[DailyOHLCVResponse])
async def get_daily_ohlcv(
    symbol: str, session: AsyncSession = Depends(get_db_session)
) -> list[DailyOHLCVResponse]:
    """Retrieve daily OHLCV bars."""
    try:
        repo = MarketDataRepository(session)
        return await repo.get_daily_ohlcv(symbol)
    except DatabaseOperationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
