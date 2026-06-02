import random
import uuid
from datetime import datetime, timezone
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.orchestrator.interfaces import ISchedulerTask
from backend.websocket.manager import ConnectionManager
from backend.websocket.schemas import WebSocketMessage
from backend.db.models.market_tick import IntradayTick

class MockIngestionTask(ISchedulerTask):
    def __init__(
        self,
        websocket_manager: ConnectionManager,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> None:
        self._name = "mock_ingestion_task"
        self.websocket_manager = websocket_manager
        self.session_maker = session_maker
        self.last_ltp = 22000.0

    @property
    def name(self) -> str:
        return self._name

    async def execute(self) -> None:
        # Generate mock market tick
        movement = random.uniform(-15.0, 15.0)
        self.last_ltp += movement
        now = datetime.now(timezone.utc)
        
        async with self.session_maker() as session:
            # Save Tick
            tick = IntradayTick(
                symbol="NIFTY 50",
                timestamp=now,
                ltp=round(self.last_ltp, 2),
                bid_price=round(self.last_ltp - 1.0, 2),
                ask_price=round(self.last_ltp + 1.0, 2),
                bid_qty=100.0,
                ask_qty=100.0,
                volume=random.randint(100, 5000),
                cold_storage_uploaded=False,
            )
            session.add(tick)
            await session.commit()
            await session.refresh(tick)
            
            # Broadcast Tick
            tick_msg = WebSocketMessage(
                event="market_tick",
                data={
                    "id": str(tick.id),
                    "symbol": tick.symbol,
                    "timestamp": tick.timestamp.isoformat(),
                    "ltp": tick.ltp,
                    "volume": tick.volume,
                }
            )
            await self.websocket_manager.broadcast(tick_msg)
            
            # Broadcast Mock Signal occasionally
            if random.random() > 0.5:
                signal_msg = WebSocketMessage(
                    event="signal_alert",
                    data={
                        "id": str(uuid.uuid4()),
                        "symbol": tick.symbol,
                        "signal": "BUY" if movement > 0 else "SELL",
                        "confidence": round(random.uniform(60, 95), 2),
                        "target_price": round(self.last_ltp + (50 if movement > 0 else -50), 2),
                        "prediction_source": "mock_model_v1",
                        "created_at": now.isoformat()
                    }
                )
                await self.websocket_manager.broadcast(signal_msg)
                
            # Broadcast Mock Portfolio occasionally
            if random.random() > 0.6:
                portfolio_msg = WebSocketMessage(
                    event="portfolio_update",
                    data={
                        "id": str(uuid.uuid4()),
                        "symbol": tick.symbol,
                        "quantity": random.randint(10, 100),
                        "average_price": round(self.last_ltp - 100, 2),
                        "current_price": round(self.last_ltp, 2),
                        "pnl": round(movement * 100, 2),
                        "last_updated": now.isoformat()
                    }
                )
                await self.websocket_manager.broadcast(portfolio_msg)
                
            # Broadcast Mock Prediction occasionally
            if random.random() > 0.8:
                model_msg = WebSocketMessage(
                    event="prediction_update",
                    data={
                        "id": str(uuid.uuid4()),
                        "model_name": "Mock_Transformer_v1",
                        "version": "1.0.0",
                        "status": "active",
                        "last_trained": now.isoformat(),
                        "accuracy_score": round(random.uniform(0.7, 0.95), 2)
                    }
                )
                await self.websocket_manager.broadcast(model_msg)
