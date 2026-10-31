"""
Models for the Cache system.

Your job: fill in the class bodies.
- Think about what metadata a cached entry needs to track
- Think about how TTL expiry is determined (created_at + ttl vs. absolute expiry?)
- Think about what statistics are useful for monitoring a cache
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import time


# ---------------------------------------------------------------------------
# Cache entry
# ---------------------------------------------------------------------------

@dataclass
class CacheEntry:
    """
    A single entry stored in the cache.

    Think about:
    - What identifies an entry? (key)
    - What data does it hold? (value)
    - What metadata is needed for eviction policies? (access_count, last_accessed)
    - How is TTL tracked? (created_at + ttl, or an absolute expiry time?)
    """
    key: str
    value: Any
    # TODO: add fields for created_at, ttl (optional), access_count, last_accessed
    # Hint: created_at and last_accessed should default to the current time
    # Hint: access_count should start at 0
    # Hint: ttl is Optional[float] — None means "no expiry"

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """
        Return True if this entry has expired based on its TTL.

        Args:
            current_time: the current time (defaults to time.time()).
                          Accepting this as a parameter allows deterministic testing.
        """
        # TODO: check if ttl is set and if created_at + ttl < current_time
        pass


# ---------------------------------------------------------------------------
# Cache statistics
# ---------------------------------------------------------------------------

@dataclass
class CacheStats:
    """
    Tracks cache performance metrics.

    Think about:
    - What counters matter? (hits, misses, evictions)
    - What state is useful? (current size, capacity)
    - How would you compute a hit ratio from these?
    """
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    # TODO: add fields for current_size and capacity

    @property
    def hit_ratio(self) -> float:
        """
        Return the cache hit ratio (hits / total requests).
        Return 0.0 if no requests have been made.
        """
        # TODO
        pass
