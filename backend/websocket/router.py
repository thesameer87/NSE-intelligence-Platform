from typing import cast
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request

from backend.utils.logger import logger
from backend.websocket.manager import ConnectionManager

router = APIRouter(prefix="/ws", tags=["WebSocket"])


def get_connection_manager(websocket: WebSocket) -> ConnectionManager:
    """Retrieve the global connection manager from app state."""
    return cast(ConnectionManager, websocket.app.state.websocket_manager)


@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket, manager: ConnectionManager = Depends(get_connection_manager)) -> None:
    """
    WebSocket endpoint for V1 streaming dashboard updates.
    """
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect inbound messages from clients in V1.
            # We just wait for disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket stream.")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket stream: {e}")
        manager.disconnect(websocket)
