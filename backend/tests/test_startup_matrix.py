import pytest
import os
import lightgbm as lgb
import numpy as np
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI
from unittest.mock import MagicMock
import pytest_asyncio
from typing import Any, AsyncGenerator

from backend.db.base import Base
from backend.db.models.prediction import ModelRegistry
from backend.persistence.prediction import PredictionRepository
from backend.engine.inference import InferenceManager

async def create_dummy_artifact(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    X = np.array([[1.0] * 16])
    y = np.array([1])
    train_data = lgb.Dataset(X, label=y)
    params = {'objective': 'binary', 'verbose': -1}
    booster = lgb.train(params, train_data, num_boost_round=1)
    booster.save_model(path)

@pytest_asyncio.fixture
async def async_session_factory() -> AsyncGenerator[Any, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    await engine.dispose()

@pytest.mark.asyncio
async def test_startup_matrix_0_models(async_session_factory: Any, tmp_path: Any) -> None:
    """Case A: 0/4 models available."""
    manager = InferenceManager()
    manager._init_once()
    
    # Empty DB
    async with async_session_factory() as session:
        repo = PredictionRepository(session)
        paths = await repo.get_active_model_paths()
        
    manager.load_models(paths)
    
    assert list(manager.model_status.values()) == [False, False, False, False]
    
@pytest.mark.asyncio
async def test_startup_matrix_2_models(async_session_factory: Any, tmp_path: Any) -> None:
    """Case B: 2/4 models available."""
    manager = InferenceManager()
    manager._init_once()
    
    path1 = str(tmp_path / "intraday_clf.txt")
    path2 = str(tmp_path / "intraday_reg.txt")
    await create_dummy_artifact(path1)
    await create_dummy_artifact(path2)
    
    async with async_session_factory() as session:
        session.add(ModelRegistry(model_name="intraday_clf", version="v1", artifact_path=path1, active=True))
        session.add(ModelRegistry(model_name="intraday_reg", version="v1", artifact_path=path2, active=True))
        await session.commit()
        
        repo = PredictionRepository(session)
        paths = await repo.get_active_model_paths()
        
    manager.load_models(paths)
    
    assert manager.model_status["intraday_clf"] is True
    assert manager.model_status["intraday_reg"] is True
    assert manager.model_status.get("nextday_clf", False) is False
    assert manager.model_status.get("nextday_reg", False) is False

@pytest.mark.asyncio
async def test_startup_matrix_4_models(async_session_factory: Any, tmp_path: Any) -> None:
    """Case C: 4/4 models available."""
    manager = InferenceManager()
    manager._init_once()
    
    models = ["intraday_clf", "intraday_reg", "nextday_clf", "nextday_reg"]
    
    async with async_session_factory() as session:
        for m in models:
            path = str(tmp_path / f"{m}.txt")
            await create_dummy_artifact(path)
            session.add(ModelRegistry(model_name=m, version="v1", artifact_path=path, active=True))
        await session.commit()
        
        repo = PredictionRepository(session)
        paths = await repo.get_active_model_paths()
        
    manager.load_models(paths)
    
    for m in models:
        assert manager.model_status[m] is True
