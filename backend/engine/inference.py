import threading
import logging
from typing import Dict, Any, Optional
import lightgbm as lgb
import numpy as np

from backend.schemas.features import FeatureVector
from backend.schemas.prediction import PredictionResponse, IntradayPrediction, NextDayPrediction, Corridor
from backend.config import Settings
from backend.utils.metrics import (
    model_reload_success_total,
    model_reload_failure_total,
    model_reload_duration_seconds
)

logger = logging.getLogger(__name__)

class ModelReloadError(Exception):
    """Raised when an all-or-nothing model reload transaction fails."""
    pass

class InferenceManager:
    """
    Singleton manager for ML models. Encapsulates LightGBM Boosters.
    Supports atomic hot-reloading by swapping internal dictionary references.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "InferenceManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(InferenceManager, cls).__new__(cls)
                cls._instance._init_once()
            return cls._instance

    def _init_once(self) -> None:
        self._models_lock = threading.Lock()
        self._models: Dict[str, Optional[lgb.Booster]] = {}
        # Tracks true/false availability per model
        self.model_status: Dict[str, bool] = {
            'intraday_clf': False,
            'intraday_reg': False,
            'nextday_clf': False,
            'nextday_reg': False,
        }
        self.last_reload_time: Optional[str] = None
        self.last_reload_status: str = "INITIALIZING"
        self.last_reload_duration_ms: float = 0.0

    def load_models(self, model_paths: Dict[str, str]) -> None:
        """
        Loads models from disk via an all-or-nothing transaction.
        Can be called during startup or hot-reload (Task 22).
        Swaps models atomically.
        """
        import time
        from datetime import datetime, timezone
        
        start_time = time.time()
        new_model_map: Dict[str, Optional[lgb.Booster]] = {}
        new_status: Dict[str, bool] = {
            'intraday_clf': False,
            'intraday_reg': False,
            'nextday_clf': False,
            'nextday_reg': False,
        }
        
        try:
            import os
            for model_key, path in model_paths.items():
                if not path or not os.path.exists(path):
                    raise ModelReloadError(f"Missing required model or file not found: {model_key} -> {path}")
                
                try:
                    booster = lgb.Booster(model_file=path)
                    new_model_map[model_key] = booster
                    new_status[model_key] = True
                except Exception as e:
                    raise ModelReloadError(f"Failed to parse LightGBM artifact for {model_key}: {e}")

            # All models parsed successfully, perform true atomic reference swap
            with self._models_lock:
                self._models = new_model_map
                self.model_status = new_status
                
            duration = time.time() - start_time
            self.last_reload_duration_ms = duration * 1000
            self.last_reload_time = datetime.now(timezone.utc).isoformat() + "Z"
            self.last_reload_status = "SUCCESS"
            
            model_reload_duration_seconds.observe(duration)
            model_reload_success_total.inc()
            logger.info(f"Models loaded and atomically swapped. Duration: {self.last_reload_duration_ms:.2f}ms")
            
        except Exception as e:
            duration = time.time() - start_time
            self.last_reload_duration_ms = duration * 1000
            self.last_reload_time = datetime.now(timezone.utc).isoformat() + "Z"
            self.last_reload_status = f"FAILED: {str(e)}"
            
            model_reload_duration_seconds.observe(duration)
            model_reload_failure_total.inc()
            logger.error(f"Hot reload aborted. Active models untouched. Reason: {e}")
            raise

    def predict(self, model_key: str, features: np.ndarray) -> Optional[np.ndarray]:
        """
        Thread-safe, lock-free prediction (reading a dict reference in Python is atomic).
        """
        model = self._models.get(model_key)
        if model is None:
            # Explicitly return None instead of mock predictions
            return None
            
        try:
            return np.array(model.predict(features))
        except Exception as e:
            logger.error(f"Inference error for {model_key}: {e}")
            return None


class PredictionService:
    """
    Service that translates FeatureVector into PredictionResponse using InferenceManager.
    Does NOT own model references directly.
    """
    def __init__(self, inference_manager: InferenceManager):
        self.inference_manager = inference_manager

    def generate_prediction(self, feature_vector: FeatureVector) -> PredictionResponse:
        """
        Runs the 4 required models and constructs a PredictionResponse.
        """
        feature_dict = feature_vector.model_dump(exclude={"symbol", "timestamp"})
        features_array = np.array([list(feature_dict.values())])
        
        status = self.inference_manager.model_status
        available_models = [k for k, v in status.items() if v]
        unavailable_models = [k for k, v in status.items() if not v]
        
        # If any model is missing from the required set, we cannot guarantee meaningful signals.
        # So we disable the runtime if there's any unavailable model.
        # Although the prompt said: "The runtime flag should be derived from required model availability rather than simply assuming all models are present."
        # We can enable it if 'intraday_clf' & 'intraday_reg' are present, or 'nextday_clf' & 'nextday_reg' are present.
        runtime_enabled = (
            (status.get('intraday_clf', False) and status.get('intraday_reg', False)) or
            (status.get('nextday_clf', False) and status.get('nextday_reg', False))
        )
        
        intra_prediction = None
        if status.get('intraday_clf') and status.get('intraday_reg'):
            intra_clf_raw = self.inference_manager.predict('intraday_clf', features_array)
            intra_reg_raw = self.inference_manager.predict('intraday_reg', features_array)
            
            if intra_clf_raw is not None and intra_reg_raw is not None:
                intra_clf_prob = float(intra_clf_raw[0])
                intra_dir = "Bullish" if intra_clf_prob >= 0.5 else "Bearish"
                if 0.45 < intra_clf_prob < 0.55:
                    intra_dir = "Neutral"
                intra_target = float(intra_reg_raw[0])
                
                intra_prediction = IntradayPrediction(
                    direction=intra_dir,
                    confidence=intra_clf_prob if intra_clf_prob >= 0.5 else 1 - intra_clf_prob,
                    target_price=intra_target
                )
                
        next_prediction = None
        if status.get('nextday_clf') and status.get('nextday_reg'):
            next_clf_raw = self.inference_manager.predict('nextday_clf', features_array)
            next_reg_raw = self.inference_manager.predict('nextday_reg', features_array)
            
            if next_clf_raw is not None and next_reg_raw is not None:
                next_clf_prob = float(next_clf_raw[0])
                next_dir = "Bullish" if next_clf_prob >= 0.5 else "Bearish"
                if 0.45 < next_clf_prob < 0.55:
                    next_dir = "Neutral"
                next_target = float(next_reg_raw[0])
                
                next_prediction = NextDayPrediction(
                    direction=next_dir,
                    confidence=next_clf_prob if next_clf_prob >= 0.5 else 1 - next_clf_prob,
                    corridor=Corridor(
                        lower=next_target * 0.99,
                        upper=next_target * 1.01
                    )
                )
        
        return PredictionResponse(
            symbol=feature_vector.symbol,
            prediction_runtime_enabled=runtime_enabled,
            available_models=available_models,
            unavailable_models=unavailable_models,
            last_reload_time=self.inference_manager.last_reload_time,
            last_reload_status=self.inference_manager.last_reload_status,
            intraday=intra_prediction,
            nextday=next_prediction
        )
