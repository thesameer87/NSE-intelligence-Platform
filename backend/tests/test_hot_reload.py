import pytest
import os
import time
import asyncio
import lightgbm as lgb
import numpy as np
from typing import Any
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from backend.engine.inference import InferenceManager, ModelReloadError
from backend.main import app

async def create_dummy_artifact(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    X = np.array([[1.0] * 16])
    y = np.array([1])
    train_data = lgb.Dataset(X, label=y)
    params = {'objective': 'binary', 'verbose': -1}
    booster = lgb.train(params, train_data, num_boost_round=1)
    booster.save_model(path)

@pytest.mark.asyncio
async def test_hot_reload_concurrent_inference(tmp_path: Any) -> None:
    """Test that concurrent inference requests are not dropped during hot reload."""
    manager = InferenceManager()
    manager._init_once()
    
    path1 = str(tmp_path / "intraday_clf.txt")
    await create_dummy_artifact(path1)
    
    # Initial load
    manager.load_models({"intraday_clf": path1})
    
    # Task to perform rapid inferences
    features = np.array([[1.0] * 16])
    successful_inferences = 0
    running = True
    
    async def inference_worker():
        nonlocal successful_inferences
        while running:
            result = manager.predict("intraday_clf", features)
            if result is not None:
                successful_inferences += 1
            await asyncio.sleep(0.001)
            
    worker_task = asyncio.create_task(inference_worker())
    
    # Yield to let the worker run
    await asyncio.sleep(0.1)
    
    # Perform hot reload
    path2 = str(tmp_path / "intraday_clf_v2.txt")
    await create_dummy_artifact(path2)
    
    start_time = time.time()
    manager.load_models({"intraday_clf": path2})
    reload_time_ms = (time.time() - start_time) * 1000
    
    running = False
    await worker_task
    
    assert successful_inferences > 0
    assert manager.last_reload_status == "SUCCESS"
    assert manager.last_reload_duration_ms > 0
    assert reload_time_ms < 5000, f"Reload took {reload_time_ms}ms, expected < 5000ms"

@pytest.mark.asyncio
async def test_hot_reload_partial_failure_rollback(tmp_path: Any) -> None:
    """Test that if a required file is missing during reload, old models are preserved."""
    manager = InferenceManager()
    manager._init_once()
    
    path1 = str(tmp_path / "intraday_clf.txt")
    await create_dummy_artifact(path1)
    
    manager.load_models({"intraday_clf": path1})
    assert manager.model_status["intraday_clf"] is True
    old_model = manager._models["intraday_clf"]
    
    with pytest.raises(ModelReloadError):
        manager.load_models({
            "intraday_clf": path1,
            "nextday_clf": str(tmp_path / "missing.txt")
        })
        
    # Verify rollback
    assert manager.model_status["intraday_clf"] is True
    assert manager._models["intraday_clf"] is old_model
    assert "FAILED" in manager.last_reload_status
    
@pytest.mark.asyncio
async def test_startup_duration() -> None:
    """Test that startup initialization duration is under 10000ms."""
    start_time = time.time()
    manager = InferenceManager()
    manager._init_once()
    startup_duration_ms = (time.time() - start_time) * 1000
    
    assert startup_duration_ms < 10000, f"Startup took {startup_duration_ms}ms, expected < 10000ms"
