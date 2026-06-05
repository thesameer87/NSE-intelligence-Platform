import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from backend.engine.signal import SignalDetector
from backend.schemas.prediction import PredictionResponse, IntradayPrediction, NextDayPrediction, Corridor

def test_signal_detector_confidence_boundary() -> None:
    settings = MagicMock()
    settings.signal_confidence_threshold = 0.75
    settings.signal_min_expected_return = 0.005
    
    detector = SignalDetector(settings)
    
    # Just below threshold
    prediction = PredictionResponse(
        symbol="RELIANCE-EQ",
        prediction_runtime_enabled=True,
        available_models=["intraday_clf", "intraday_reg"],
        unavailable_models=[],
        intraday=IntradayPrediction(
            direction="Bullish",
            confidence=0.74, # Less than 0.75
            target_price=105.0
        ),
        nextday=None
    )
    
    # Should drop
    signal = detector.evaluate(prediction, last_price=100.0)
    assert signal is None
    
    # Exactly at threshold
    prediction.intraday.confidence = 0.75 # type: ignore
    signal2 = detector.evaluate(prediction, last_price=100.0)
    assert signal2 is not None
    assert signal2.signal == "BUY"

def test_signal_detector_alignment_boundary() -> None:
    settings = MagicMock()
    settings.signal_confidence_threshold = 0.75
    settings.signal_min_expected_return = 0.005
    
    detector = SignalDetector(settings)
    
    # Bullish but target is below current price
    prediction = PredictionResponse(
        symbol="RELIANCE-EQ",
        prediction_runtime_enabled=True,
        available_models=[],
        unavailable_models=[],
        intraday=IntradayPrediction(
            direction="Bullish",
            confidence=0.80,
            target_price=95.0 # Below last_price=100
        ),
        nextday=None
    )
    
    signal = detector.evaluate(prediction, last_price=100.0)
    assert signal is None
