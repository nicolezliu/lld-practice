"""
Core Cache logic.

Your job: implement the Cache class.
This is the main entry point — it orchestrates entries, eviction, TTL, and stats.

Think about:
- How do you handle TTL expiry? (lazy expiration on access)
- How do you wire the eviction policy hooks correctly?
- When do you increment hit vs miss counters?
- What happens when you put() a key that already exists? (update, not insert)
"""

from typing import Any, Optional, Callable
import time

from models import CacheEntry, CacheStats
from eviction import EvictionPolicy


class Cache:
    """
    A key-value cache with configurable eviction policy and optional TTL.

    Uses lazy expiration: expired entries are only removed when accessed.
    A clock function is injected for deterministic testing.
    """

    def __init__(
        self,
        capacity: int,
        eviction_policy: EvictionPolicy,
        clock: Callable[[], float] = time.time,
    ):
        """
        Args:
            capacity: maximum number of entries the cache can hold
            eviction_policy: the eviction strategy to use (LRU, LFU, etc.)
            clock: callable returning current time in seconds (injectable for testing)
        """
        # TODO:
        # - store capacity, eviction_policy, clock
        # - initialize the data store (dict of key → CacheEntry)
        # - initialize stats counters (hits, misses, evictions)
        pass

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.

        Returns:
            The cached value, or None if the key is not found or has expired.

        Side effects:
            - Increments hit or miss counter
            - Notifies the eviction policy on access (hit)
            - Lazily removes expired entries
        """
        # TODO:
        # 1. Check if key exists in the store
        # 2. If not found → increment misses, return None
        # 3. If found but expired → remove it (delete + eviction policy remove), increment misses, return None
        # 4. If found and valid → increment hits, update entry.last_accessed and access_count,
        #    notify eviction policy (on_access), return the value
        pass

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Insert or update a key-value pair in the cache.

        If the key already exists, update the value (and reset TTL if provided).
        If the cache is full, evict according to the eviction policy.

        Args:
            key: the cache key
            value: the value to store
            ttl: time-to-live in seconds (None = no expiry)
        """
        # TODO:
        # 1. If key already exists → update the value, reset created_at for new TTL,
        #    notify eviction policy (on_access), return
        # 2. If cache is full → evict one entry (eviction policy.evict()),
        #    remove evicted entry from store, increment evictions counter
        # 3. Create a new CacheEntry with current time from clock
        # 4. Store the entry
        # 5. Notify eviction policy (on_insert)
        pass

    def delete(self, key: str) -> bool:
        """
        Explicitly remove a key from the cache.

        Returns:
            True if the key was found and removed, False otherwise.
        """
        # TODO:
        # 1. If key not in store → return False
        # 2. Remove from store and eviction policy
        # 3. Return True
        pass

    def clear(self) -> None:
        """Remove all entries from the cache."""
        # TODO: clear the store and reset the eviction policy state
        pass

    def stats(self) -> CacheStats:
        """Return current cache statistics."""
        # TODO: return a CacheStats instance with current counters
        pass

    def __len__(self) -> int:
        """Return the number of entries currently in the cache."""
        # TODO
        pass

    def __contains__(self, key: str) -> bool:
        """Return True if the key is in the cache and not expired."""
        # TODO: check existence and expiry without affecting stats
        pass
