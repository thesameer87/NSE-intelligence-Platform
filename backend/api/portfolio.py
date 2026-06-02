from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dependencies import get_db_session
from backend.persistence.exceptions import DatabaseOperationError
from backend.persistence.portfolio import PortfolioRepository
from backend.schemas.portfolio import PortfolioHoldingResponse

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get("/holdings", response_model=list[PortfolioHoldingResponse])
async def get_holdings(
    session: AsyncSession = Depends(get_db_session),
) -> list[PortfolioHoldingResponse]:
    """Retrieve portfolio holdings."""
    try:
        repo = PortfolioRepository(session)
        return await repo.get_holdings()
    except DatabaseOperationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )
