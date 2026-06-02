from typing import Any
from pydantic import BaseModel, Field


class WebSocketMessage(BaseModel):
    """
    Standardized payload envelope for all outbound WebSocket broadcasts.
    """

    event: str = Field(..., description="The type of the event being broadcast")
    data: dict[str, Any] = Field(default_factory=dict, description="The payload data")
