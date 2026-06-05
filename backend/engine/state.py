from collections import deque
import threading
from typing import Dict, List, Optional
from backend.config import Settings
from backend.ingestion.schemas import NormalizedTick

class RollingStateManager:
    """
    Manages a memory-bounded ring buffer of recent market ticks for each symbol.
    Provides O(1) append operations and thread-safe read/write access.
    """
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._window_size = settings.rolling_window_size
        # Dictionary of deques: symbol -> deque of NormalizedTick
        self._buffers: Dict[str, deque[NormalizedTick]] = {}
        # Simple lock for thread-safe dictionary access and appending
        self._lock = threading.Lock()

    def append_tick(self, tick: NormalizedTick) -> None:
        """
        Appends a tick to the rolling window for its symbol.
        Automatically evicts oldest ticks if maxlen is reached.
        """
        symbol = tick.symbol
        with self._lock:
            if symbol not in self._buffers:
                self._buffers[symbol] = deque(maxlen=self._window_size)
            self._buffers[symbol].append(tick)

    def get_window(self, symbol: str) -> List[NormalizedTick]:
        """
        Returns a snapshot (list) of the current window for the given symbol.
        Returns an empty list if the symbol is not found.
        """
        with self._lock:
            if symbol not in self._buffers:
                return []
            return list(self._buffers[symbol])

    def get_latest_tick(self, symbol: str) -> Optional[NormalizedTick]:
        """
        Returns the most recent tick for a symbol, or None if empty.
        """
        with self._lock:
            if symbol not in self._buffers or len(self._buffers[symbol]) == 0:
                return None
            return self._buffers[symbol][-1]
