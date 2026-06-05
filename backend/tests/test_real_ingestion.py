import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from backend.orchestrator.real_task import RealIngestionTask
from backend.ingestion.schemas import NormalizedTick
from typing import Any
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_inference_failure_does_not_stop_tick_persistence() -> None:
    """
    Proves that if PredictionService or FeatureEngine fails during the pipeline,
    the tick is still persisted to the database and broadcasted.
    """
    settings = MagicMock()
    settings.monitored_symbols = ["RELIANCE-EQ"]
    
    websocket_manager = AsyncMock()
    session_maker = MagicMock()
    
    # Mock the async context manager for session
    session_mock = AsyncMock()
    session_maker.return_value.__aenter__.return_value = session_mock
    
    rolling_state = MagicMock()
    rolling_state.get_window.return_value = []
    
    prediction_service = MagicMock()
    # Force inference failure
    prediction_service.generate_prediction.side_effect = Exception("Simulated inference failure")
    
    signal_detector = MagicMock()
    
    # We need to mock SmartAPIClient so it returns a tick
    # The client is instantiated via async with inside execute, we patch it
    with pytest.MonkeyPatch.context() as m:
        client_mock = AsyncMock()
        client_mock.get_ltp.return_value = NormalizedTick(
            symbol="RELIANCE-EQ",
            timestamp=datetime.now(timezone.utc),
            last_price=2500.0,
            volume=100
        )
        
        class MockClientContext:
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                pass
            async def __aenter__(self) -> AsyncMock:
                return client_mock
            async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                pass
                
        m.setattr("backend.orchestrator.real_task.SmartAPIClient", MockClientContext)
        
        # We also need to prevent FeatureEngine from complaining about empty window since we mock it
        m.setattr("backend.orchestrator.real_task.FeatureEngine.compute_features", MagicMock())
        
        task = RealIngestionTask(
            settings=settings,
            websocket_manager=websocket_manager,
            session_maker=session_maker,
            rolling_state=rolling_state,
            prediction_service=prediction_service,
            signal_detector=signal_detector
        )
        
        await task.execute()
        
        # Assertions
        # 1. Tick should be appended to state
        assert rolling_state.append_tick.call_count == 1
        
        # 2. Prediction should be called and fail
        # Wait, since feature_engine is mocked, prediction is called with its return value
        assert prediction_service.generate_prediction.call_count == 1
        
        # 3. Tick MUST still be added to session and committed
        assert session_mock.add.call_count == 1
        # The first argument to add should be the IntradayTick
        added_obj = session_mock.add.call_args[0][0]
        assert added_obj.symbol == "RELIANCE-EQ"
        assert added_obj.ltp == 2500.0
        
        assert session_mock.commit.call_count == 1
        
        # 4. Tick must be broadcasted
        assert websocket_manager.broadcast.call_count == 1
        broadcast_msg = websocket_manager.broadcast.call_args[0][0]
        assert broadcast_msg.event == "market_tick"
        assert broadcast_msg.data["symbol"] == "RELIANCE-EQ"

@pytest.mark.asyncio
async def test_disabled_prediction_runtime_broadcast() -> None:
    """
    Proves that if models are unavailable, prediction_runtime_enabled is false,
    and prediction_update is broadcasted with degraded state.
    """
    settings = MagicMock()
    settings.monitored_symbols = ["TCS-EQ"]
    
    websocket_manager = AsyncMock()
    session_maker = MagicMock()
    session_mock = AsyncMock()
    session_maker.return_value.__aenter__.return_value = session_mock
    
    rolling_state = MagicMock()
    
    prediction_service = MagicMock()
    # Mock a disabled response
    from backend.schemas.prediction import PredictionResponse
    prediction_service.generate_prediction.return_value = PredictionResponse(
        symbol="TCS-EQ",
        prediction_runtime_enabled=False,
        available_models=[],
        unavailable_models=["intraday_clf", "intraday_reg"],
        intraday=None,
        nextday=None
    )
    
    signal_detector = MagicMock()
    signal_detector.evaluate.return_value = None
    
    with pytest.MonkeyPatch.context() as m:
        client_mock = AsyncMock()
        client_mock.get_ltp.return_value = NormalizedTick(
            symbol="TCS-EQ",
            timestamp=datetime.now(timezone.utc),
            last_price=3500.0,
            volume=200
        )
        
        class MockClientContext:
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                pass
            async def __aenter__(self) -> AsyncMock:
                return client_mock
            async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
                pass
                
        m.setattr("backend.orchestrator.real_task.SmartAPIClient", MockClientContext)
        m.setattr("backend.orchestrator.real_task.FeatureEngine.compute_features", MagicMock())
        
        task = RealIngestionTask(
            settings=settings,
            websocket_manager=websocket_manager,
            session_maker=session_maker,
            rolling_state=rolling_state,
            prediction_service=prediction_service,
            signal_detector=signal_detector
        )
        
        await task.execute()
        
        # 1. Tick is broadcasted
        # 2. Prediction update is broadcasted with disabled state
        assert websocket_manager.broadcast.call_count == 2
        calls = websocket_manager.broadcast.call_args_list
        tick_msg = calls[0][0][0]
        pred_msg = calls[1][0][0]
        
        assert tick_msg.event == "market_tick"
        assert pred_msg.event == "prediction_update"
        assert pred_msg.data["prediction_runtime_enabled"] is False
        assert pred_msg.data["unavailable_models"] == ["intraday_clf", "intraday_reg"]
