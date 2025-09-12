# Purpose: Tiny in-memory TTL cache for provider responses (to reduce API costs/latency)
import time                                            # For expiration timestamps
from typing import Any, Dict, Tuple                    # Typing helpers


class TTLCache:
    """
    Simple TTL cache with string keys. Not thread-safe (fine for dev).
    For production, consider Redis or an in-process LRU with locks.
    """
    def __init__(self, ttl_seconds: int = 900) -> None:
        self.ttl = ttl_seconds                         # Default time-to-live (e.g., 15min)
        self.store: Dict[str, Tuple[float, Any]] = {}  # Map: key -> (expiry_ts, value)

    def get(self, key: str) -> Any | None:
        now = time.time()                              # Current time
        rec = self.store.get(key)                      # Lookup record
        if not rec:                                    # Not found -> miss
            return None
        exp, value = rec                               # Unpack expiry and value
        if now > exp:                                  # Expired -> delete and miss
            del self.store[key]
            return None
        return value                                   # Valid -> hit

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl_eff = ttl if ttl is not None else self.ttl # Use provided TTL or default
        self.store[key] = (time.time() + ttl_eff, value)  # Save with expiry


# Global cache instance (fine for our use)
cache = TTLCache(ttl_seconds=900)
