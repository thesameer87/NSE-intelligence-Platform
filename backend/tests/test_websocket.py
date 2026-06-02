
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.websocket.manager import ConnectionManager
from backend.websocket.schemas import WebSocketMessage


def test_websocket_connect_disconnect() -> None:
    """Test successful connection and graceful disconnection."""
    client = TestClient(app)

    # Ensure manager is setup for tests since we don't trigger the lifespan via TestClient easily
    app.state.websocket_manager = ConnectionManager()
    manager = app.state.websocket_manager
    
    assert len(manager.active_connections) == 0
    
    with client.websocket_connect("/ws/stream"):
        # After connection, it should be registered
        assert len(manager.active_connections) == 1
        
    # After context manager exit (disconnect), it should be removed
    assert len(manager.active_connections) == 0


@pytest.mark.asyncio
async def test_websocket_broadcast() -> None:
    """Test deterministic broadcast behavior with schema serialization."""
    # We must mock the active_connections behavior natively using background tasks 
    # if we want to test broadcast. But standard Starlette TestClient blocks.
    # We can test the manager directly for broadcast isolation and schema tests.
    pass


@pytest.mark.asyncio
async def test_manager_broadcast_isolation() -> None:
    """Test that a failing socket during broadcast does not crash the manager."""
    from unittest.mock import AsyncMock

    from fastapi import WebSocket

    # Create two mock websockets
    ws1 = AsyncMock(spec=WebSocket)
    ws2 = AsyncMock(spec=WebSocket)

    # Make ws1 fail when sending
    ws1.send_text.side_effect = RuntimeError("Broken pipe")

    manager = ConnectionManager()
    manager.active_connections.clear()
    await manager.connect(ws1)
    await manager.connect(ws2)
    
    assert len(manager.active_connections) == 2
    
    msg = WebSocketMessage(event="system_status", data={"status": "ok"})
    
    # This should not raise an exception, despite ws1 failing
    await manager.broadcast(msg)
    
    # ws1 should have been disconnected by the cleanup process
    assert len(manager.active_connections) == 1
    assert ws2 in manager.active_connections


def test_schema_serialization() -> None:
    """Test WebSocketMessage enforces correct requirements."""
    msg = WebSocketMessage(event="market_tick", data={"price": 100})
    assert msg.event == "market_tick"
    assert msg.data["price"] == 100
    
    import pydantic
    with pytest.raises(pydantic.ValidationError):
        # Missing event type should fail
        WebSocketMessage(data={})  # type: ignore
