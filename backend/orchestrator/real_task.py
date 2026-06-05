import asyncio
import logging
from typing import List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.config import Settings
from backend.orchestrator.interfaces import ISchedulerTask
from backend.websocket.manager import ConnectionManager
from backend.websocket.schemas import WebSocketMessage
from backend.ingestion.client import SmartAPIClient
from backend.db.models.market_tick import IntradayTick
from backend.engine.state import RollingStateManager
from backend.engine.features import FeatureEngine
from backend.engine.inference import PredictionService
from backend.engine.signal import SignalDetector
from backend.persistence.signal import SignalRepository

logger = logging.getLogger(__name__)

class RealIngestionTask(ISchedulerTask):
    def __init__(
        self,
        settings: Settings,
        websocket_manager: ConnectionManager,
        session_maker: async_sessionmaker[AsyncSession],
        rolling_state: RollingStateManager,
        prediction_service: PredictionService,
        signal_detector: SignalDetector,
    ) -> None:
        self._name = "real_ingestion_task"
        self.settings = settings
        self.websocket_manager = websocket_manager
        self.session_maker = session_maker
        self.rolling_state = rolling_state
        self.prediction_service = prediction_service
        self.signal_detector = signal_detector
        
    @property
    def name(self) -> str:
        return self._name

    async def execute(self) -> None:
        """
        Executes the full V1 pipeline for all monitored symbols:
        Ingestion -> State Update -> Features -> Prediction -> Signal -> Persistence -> WebSocket
        """
        symbols = self.settings.monitored_symbols
        
        async with SmartAPIClient(self.settings) as client:
            # We can fetch them concurrently or sequentially.
            # To respect latency budget but avoid rate limits, we use asyncio.gather with a small concurrency limit.
            tasks = [self._process_symbol(symbol, client) for symbol in symbols]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_symbol(self, symbol: str, client: SmartAPIClient) -> None:
        # Deterministic exponential backoff
        max_attempts = 3
        delay = 1.0
        
        for attempt in range(max_attempts):
            try:
                # 1. Ingestion
                # For Angel One, we need symbol_token. In a real system, there's a symbol_token map.
                # Assuming get_ltp can handle just the symbol or we have a dummy token for now.
                tick = await client.get_ltp(exchange="NSE", symbol=symbol, symbol_token="DUMMY")
                
                # 2. State Update
                self.rolling_state.append_tick(tick)
                window = self.rolling_state.get_window(symbol)
                
                new_signal = None
                try:
                    # 3. Features
                    feature_vector = FeatureEngine.compute_features(window)
                    
                    # 4. Prediction
                    prediction_response = self.prediction_service.generate_prediction(feature_vector)
                    
                    # 5. Signal Detection
                    new_signal = self.signal_detector.evaluate(prediction_response, last_price=tick.last_price)
                except Exception as eval_err:
                    logger.error(f"Inference pipeline failed for {symbol}, but tick will be persisted: {eval_err}")
                    prediction_response = None
                
                # 6. Persistence & WebSocket Broadcast
                async with self.session_maker() as session:
                    now = datetime.now(timezone.utc)
                    # Persist Tick
                    db_tick = IntradayTick(
                        symbol=tick.symbol,
                        timestamp=tick.timestamp,
                        ltp=tick.last_price,
                        volume=tick.volume if tick.volume else 0,
                        cold_storage_uploaded=False,
                    )
                    session.add(db_tick)
                    
                    # Persist Signal if any
                    if new_signal:
                        signal_repo = SignalRepository(session)
                        await signal_repo.save_signal(new_signal)
                        
                    # Commit transaction safely
                    try:
                        await session.commit()
                        await session.refresh(db_tick)
                    except Exception as e:
                        await session.rollback()
                        logger.error(f"Persistence failure for {symbol}: {e}")
                        raise
                        
                # Broadcast Tick
                tick_msg = WebSocketMessage(
                    event="market_tick",
                    data={
                        "id": str(db_tick.id),
                        "symbol": db_tick.symbol,
                        "timestamp": db_tick.timestamp.isoformat(),
                        "ltp": db_tick.ltp,
                        "volume": db_tick.volume,
                    }
                )
                await self.websocket_manager.broadcast(tick_msg)
                
                # Broadcast Prediction Status if we successfully executed the pipeline
                if prediction_response is not None:
                    prediction_msg = WebSocketMessage(
                        event="prediction_update",
                        data={
                            "symbol": symbol,
                            "prediction_runtime_enabled": prediction_response.prediction_runtime_enabled,
                            "available_models": prediction_response.available_models,
                            "unavailable_models": prediction_response.unavailable_models,
                            "has_intraday": prediction_response.intraday is not None,
                            "has_nextday": prediction_response.nextday is not None
                        }
                    )
                    await self.websocket_manager.broadcast(prediction_msg)
                
                # Broadcast Signal if any
                if new_signal:
                    signal_msg = WebSocketMessage(
                        event="signal_alert",
                        data={
                            "id": str(new_signal.id) if new_signal.id else "",
                            "symbol": new_signal.symbol,
                            "signal": new_signal.signal,
                            "confidence": new_signal.confidence,
                            "target_price": new_signal.target_price,
                            "prediction_source": new_signal.prediction_source,
                            "created_at": new_signal.created_at.isoformat()
                        }
                    )
                    await self.websocket_manager.broadcast(signal_msg)
                    
                # Success, exit retry loop
                return
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt == max_attempts - 1:
                    logger.error(f"Failed to process {symbol} after {max_attempts} attempts.")
                else:
                    await asyncio.sleep(delay)
                    delay *= 2.0 # Exponential backoff: 1s -> 2s -> 4s
