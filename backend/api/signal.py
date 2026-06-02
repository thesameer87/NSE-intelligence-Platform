from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dependencies import get_db_session
from backend.persistence.exceptions import DatabaseOperationError
from backend.persistence.signal import SignalRepository
from backend.schemas.signal import TradingSignalResponse

router = APIRouter(prefix="/signal", tags=["Trading Signals"])


@router.get("/", response_model=list[TradingSignalResponse])
async def get_signals(
    session: AsyncSession = Depends(get_db_session),
) -> list[TradingSignalResponse]:
    """Retrieve generated trading signals."""
    try:
        repo = SignalRepository(session)
        return await repo.get_signals()
    except DatabaseOperationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
