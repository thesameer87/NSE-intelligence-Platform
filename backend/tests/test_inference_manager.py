import pytest
import os
import numpy as np
from backend.engine.inference import InferenceManager, ModelReloadError

def test_inference_manager_missing_models() -> None:
    """Test that missing files trigger a ModelReloadError."""
    manager = InferenceManager()
    manager._init_once()
    
    with pytest.raises(ModelReloadError):
        manager.load_models({
            'intraday_clf': 'invalid/path/intraday_clf.txt',
            'nextday_clf': 'invalid/path/nextday_clf.txt'
        })
    
    assert manager.model_status['intraday_clf'] is False
    assert manager._models.get('intraday_clf') is None

def test_inference_manager_corrupted_models(tmp_path: str) -> None:
    """Test that corrupted files trigger a ModelReloadError."""
    manager = InferenceManager()
    manager._init_once()
    
    bad_path = os.path.join(tmp_path, "corrupted.txt")
    with open(bad_path, "w") as f:
        f.write("invalid lgb data")
        
    with pytest.raises(ModelReloadError):
        manager.load_models({
            'intraday_clf': bad_path
        })
    
    assert manager.model_status['intraday_clf'] is False
    assert manager._models.get('intraday_clf') is None

def test_inference_manager_valid_model(tmp_path: str) -> None:
    """Test that a valid LightGBM .txt file is successfully loaded."""
    manager = InferenceManager()
    manager._init_once()
    
    valid_path = os.path.join(tmp_path, "valid.txt")
    import lightgbm as lgb
    X = np.array([[1.0] * 16])
    y = np.array([1])
    train_data = lgb.Dataset(X, label=y)
    params = {'objective': 'binary', 'verbose': -1}
    booster = lgb.train(params, train_data, num_boost_round=1)
    booster.save_model(valid_path)
    
    manager.load_models({'intraday_clf': valid_path})
    
    assert manager.model_status['intraday_clf'] is True
    assert manager._models['intraday_clf'] is not None
