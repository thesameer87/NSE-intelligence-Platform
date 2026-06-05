import logging
from typing import Optional
from datetime import datetime, timezone

from backend.config import Settings
from backend.schemas.prediction import PredictionResponse
from backend.db.models.signal import TradingSignal

logger = logging.getLogger(__name__)

class SignalDetector:
    """
    Evaluates ML predictions against configured thresholds to generate actionable trading signals.
    """
    def __init__(self, settings: Settings):
        self.settings = settings

    def evaluate(self, prediction: PredictionResponse, last_price: float) -> Optional[TradingSignal]:
        """
        Evaluates a PredictionResponse and returns a TradingSignal if thresholds are met.
        Returns None if the signal is HOLD or dropped.
        """
        # If prediction runtime is completely disabled or intraday is missing, return None.
        if not prediction.prediction_runtime_enabled or prediction.intraday is None:
            return None

        intra = prediction.intraday
        direction = intra.direction
        confidence = intra.confidence
        target_price = intra.target_price
        
        # 1. Check confidence threshold
        if confidence < self.settings.signal_confidence_threshold:
            logger.debug(f"Signal dropped for {prediction.symbol}: Confidence {confidence:.2f} < {self.settings.signal_confidence_threshold:.2f}")
            return None
            
        if direction not in ("Bullish", "Bearish"):
            return None
            
        # 2. Check minimum expected return
        if last_price <= 0:
            return None
            
        expected_return = abs(target_price - last_price) / last_price
        if expected_return < self.settings.signal_min_expected_return:
            logger.debug(f"Signal dropped for {prediction.symbol}: Expected return {expected_return:.4f} < {self.settings.signal_min_expected_return:.4f}")
            return None
            
        # 3. Check regression alignment
        # If Bullish, target must be > last_price
        # If Bearish, target must be < last_price
        is_aligned = (direction == "Bullish" and target_price > last_price) or \
                     (direction == "Bearish" and target_price < last_price)
                     
        if not is_aligned:
            logger.debug(f"Signal dropped for {prediction.symbol}: Direction {direction} misaligned with target {target_price} vs last {last_price}")
            return None

        # Determine signal action
        signal_action = "BUY" if direction == "Bullish" else "SELL"

        # Construct and return the database model instance
        return TradingSignal(
            symbol=prediction.symbol,
            signal=signal_action,
            confidence=confidence,
            target_price=target_price,
            prediction_source="lgbm_v1",
            created_at=datetime.now(timezone.utc)
        )
