from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dependencies import get_db_session
from backend.persistence.exceptions import DatabaseOperationError
from backend.persistence.prediction import PredictionRepository
from backend.schemas.prediction import ModelRegistryResponse, PredictionResponse

router = APIRouter(prefix="/prediction", tags=["Predictions"])


@router.get("/models/latest", response_model=list[ModelRegistryResponse])
async def get_latest_models(
    session: AsyncSession = Depends(get_db_session),
) -> list[ModelRegistryResponse]:
    """Retrieve registered ML models."""
    try:
        repo = PredictionRepository(session)
        return await repo.get_latest_models()
    except DatabaseOperationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


@router.get("/{symbol}", response_model=PredictionResponse)
async def get_prediction(symbol: str) -> PredictionResponse:
    """Retrieve predictions for a symbol."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No prediction data found for {symbol}",
    )
