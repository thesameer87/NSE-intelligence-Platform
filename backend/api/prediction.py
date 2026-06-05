from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.dependencies import get_db_session
from backend.persistence.exceptions import DatabaseOperationError
from backend.persistence.prediction import PredictionRepository
from backend.schemas.prediction import ModelRegistryResponse, PredictionResponse, ModelLatestResponse
from backend.engine.inference import InferenceManager

router = APIRouter(prefix="/prediction", tags=["Predictions"])


@router.get("/models/latest", response_model=ModelLatestResponse)
async def get_latest_models(
    session: AsyncSession = Depends(get_db_session),
) -> ModelLatestResponse:
    """Retrieve registered ML models and hot-reload status."""
    try:
        repo = PredictionRepository(session)
        models = await repo.get_latest_models()
        
        manager = InferenceManager()
        return ModelLatestResponse(
            last_reload_time=manager.last_reload_time,
            last_reload_status=manager.last_reload_status,
            last_reload_duration_ms=manager.last_reload_duration_ms,
            models=models
        )
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
