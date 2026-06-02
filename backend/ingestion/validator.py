from datetime import datetime, timezone
from typing import Any

from backend.ingestion.exceptions import IngestionValidationError
from backend.ingestion.schemas import NormalizedTick


def normalize_ltp_payload(symbol: str, data: dict[str, Any]) -> NormalizedTick:
    """
    Validates and normalizes a SmartAPI LTP response into a NormalizedTick.
    """
    try:
        last_price = float(data["ltp"])

        # Typically SmartAPI does not return volume in standard LTP requests,
        # so we properly assign None to preserve semantics rather than mutating to 0.
        volume = int(data["volume"]) if "volume" in data and data["volume"] is not None else None
        
        return NormalizedTick(
            symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            last_price=last_price,
            volume=volume,
        )
    except (KeyError, ValueError, TypeError) as e:
        raise IngestionValidationError(f"Failed to normalize LTP payload for {symbol}: {e}")
