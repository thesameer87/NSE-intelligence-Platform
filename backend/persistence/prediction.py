from typing import Protocol, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from backend.db.models.prediction import ModelRegistry
from backend.schemas.prediction import ModelRegistryResponse
from backend.persistence.exceptions import DatabaseOperationError
from backend.utils.logger import logger


class IPredictionRepository(Protocol):
    """Protocol for prediction persistence operations."""
    async def get_latest_models(self) -> list[ModelRegistryResponse]: ...


class PredictionRepository:
    """Concrete implementation of IPredictionRepository."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_latest_models(self) -> list[ModelRegistryResponse]:
        """Fetch latest models from registry."""
        try:
            stmt = select(ModelRegistry).order_by(ModelRegistry.trained_at.desc())
            result = await self.session.execute(stmt)
            models = result.scalars().all()
            
            return [
                ModelRegistryResponse(
                    model_name=m.model_name,
                    version=m.version,
                    metrics_json=m.metrics_json,
                    schema_version=m.schema_version,
                    trained_at=m.trained_at,
                )
                for m in models
            ]
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch models: {e}")
            raise DatabaseOperationError("Database error while fetching models") from e
