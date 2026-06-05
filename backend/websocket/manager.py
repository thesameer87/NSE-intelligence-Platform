from fastapi import WebSocket

from backend.utils.logger import logger
from backend.websocket.schemas import WebSocketMessage
from backend.utils.metrics import websocket_connections


class ConnectionManager:
    """
    Manages active WebSocket connections and handles async-safe broadcasting.
    """

    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        websocket_connections.inc()
        logger.info(f"WebSocket connection accepted. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected WebSocket from the active set."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            websocket_connections.dec()
            logger.info(f"WebSocket connection removed. Total active: {len(self.active_connections)}")

    async def broadcast(self, message: WebSocketMessage) -> None:
        """
        Broadcast a structured message to all active connections.
        Ensures deterministic failure isolation 
        (one failed socket won't crash the broadcast).
        """
        if not self.active_connections:
            return

        payload = message.model_dump_json()
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.exception(f"Failed to send message to websocket: {e}")
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)
