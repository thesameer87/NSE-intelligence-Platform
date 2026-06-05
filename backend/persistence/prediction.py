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
    async def get_active_model_paths(self) -> dict[str, str]: ...


class PredictionRepository:
    """Concrete implementation of IPredictionRepository."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_latest_models(self) -> list[ModelRegistryResponse]:
        """Fetch latest active models from registry."""
        try:
            stmt = select(ModelRegistry).where(ModelRegistry.active == True).order_by(ModelRegistry.created_at.desc())
            result = await self.session.execute(stmt)
            models = result.scalars().all()
            
            return [
                ModelRegistryResponse(
                    model_name=m.model_name,
                    version=m.version,
                    artifact_path=m.artifact_path,
                    active=m.active,
                    created_at=m.created_at,
                )
                for m in models
            ]
        except SQLAlchemyError as e:
            logger.error(f"Failed to fetch models: {e}")
            raise DatabaseOperationError("Database error while fetching models") from e

    async def get_active_model_paths(self) -> dict[str, str]:
        """
        Returns a dictionary mapping model_name to artifact_path
        for all currently active models.
        """
        models = await self.get_latest_models()
        
        # Deduplicate to ensure we only return the latest active version per model_name
        paths: dict[str, str] = {}
        for m in models:
            if m.model_name not in paths:
                paths[m.model_name] = m.artifact_path
                
        return paths
