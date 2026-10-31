"""
SOLUTION — Cache System (LRU/LFU)

Don't peek until you've given it a solid attempt!

This is one valid solution. Yours may differ in structure and still be
perfectly correct — there's no single "right" LLD answer. Compare your
design choices against this one and think about trade-offs.

Key design decisions:
1. LRU uses collections.OrderedDict — O(1) move_to_end and popitem.
2. LFU uses a frequency map + OrderedDict per frequency bucket — O(1)
   access, insert, and eviction with LRU tie-breaking within each bucket.
3. TTL uses lazy expiration: entries are only removed when accessed.
   A clock callable is injected for deterministic testing.
4. The Cache class delegates all eviction decisions to the EvictionPolicy,
   keeping the cache logic clean and the policy swappable.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from collections import OrderedDict
import time


# ===================================================================
# Models
# ===================================================================

@dataclass
class CacheEntry:
    """A single entry stored in the cache."""
    key: str
    value: Any
    created_at: float
    ttl: Optional[float] = None
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """Return True if this entry has exceeded its TTL."""
        if self.ttl is None:
            return False
        if current_time is None:
            current_time = time.time()
        return current_time >= self.created_at + self.ttl


@dataclass
class CacheStats:
    """Tracks cache performance metrics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    current_size: int = 0
    capacity: int = 0

    @property
    def hit_ratio(self) -> float:
        """Return hits / total_requests, or 0.0 if no requests."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total


# ===================================================================
# Eviction policies (Strategy pattern)
# ===================================================================

class EvictionPolicy(ABC):
    """Abstract eviction policy."""

    @abstractmethod
    def on_access(self, key: str) -> None:
        ...

    @abstractmethod
    def on_insert(self, key: str) -> None:
        ...

    @abstractmethod
    def evict(self) -> Optional[str]:
        ...

    @abstractmethod
    def remove(self, key: str) -> None:
        ...


class LRUPolicy(EvictionPolicy):
    """
    Least Recently Used — O(1) via OrderedDict.

    OrderedDict maintains insertion order and supports O(1):
    - move_to_end(key)      → mark as most recently used
    - popitem(last=False)   → evict the least recently used
    """

    def __init__(self):
        self._order: OrderedDict[str, None] = OrderedDict()

    def on_access(self, key: str) -> None:
        if key in self._order:
            self._order.move_to_end(key)

    def on_insert(self, key: str) -> None:
        self._order[key] = None

    def evict(self) -> Optional[str]:
        if not self._order:
            return None
        key, _ = self._order.popitem(last=False)
        return key

    def remove(self, key: str) -> None:
        self._order.pop(key, None)


class LFUPolicy(EvictionPolicy):
    """
    Least Frequently Used — O(1) via frequency buckets.

    Data structures:
    - _key_freq: dict[str, int] — maps each key to its current frequency
    - _freq_keys: dict[int, OrderedDict[str, None]] — maps each frequency
      to an OrderedDict of keys at that frequency (preserves insertion
      order for LRU tie-breaking within the same frequency)
    - _min_freq: int — the current minimum frequency across all keys

    on_insert: new key gets freq=1, min_freq resets to 1.
    on_access: move key from freq bucket to freq+1 bucket.
    evict: pop the oldest key from _freq_keys[_min_freq].
    """

    def __init__(self):
        self._key_freq: dict[str, int] = {}
        self._freq_keys: dict[int, OrderedDict[str, None]] = {}
        self._min_freq: int = 0

    def on_access(self, key: str) -> None:
        if key not in self._key_freq:
            return

        freq = self._key_freq[key]

        # Remove from current frequency bucket
        self._freq_keys[freq].pop(key)
        if not self._freq_keys[freq]:
            del self._freq_keys[freq]
            if self._min_freq == freq:
                self._min_freq = freq + 1

        # Add to next frequency bucket
        new_freq = freq + 1
        self._key_freq[key] = new_freq
        if new_freq not in self._freq_keys:
            self._freq_keys[new_freq] = OrderedDict()
        self._freq_keys[new_freq][key] = None

    def on_insert(self, key: str) -> None:
        self._key_freq[key] = 1
        if 1 not in self._freq_keys:
            self._freq_keys[1] = OrderedDict()
        self._freq_keys[1][key] = None
        self._min_freq = 1

    def evict(self) -> Optional[str]:
        if not self._key_freq:
            return None

        # Get the bucket with the minimum frequency
        bucket = self._freq_keys.get(self._min_freq)
        if not bucket:
            return None

        # Pop the oldest key (FIFO for tie-breaking)
        key, _ = bucket.popitem(last=False)
        if not bucket:
            del self._freq_keys[self._min_freq]
            # Update min_freq to the next available frequency
            if self._freq_keys:
                self._min_freq = min(self._freq_keys)

        del self._key_freq[key]
        return key

    def remove(self, key: str) -> None:
        if key not in self._key_freq:
            return

        freq = self._key_freq[key]
        del self._key_freq[key]

        if freq in self._freq_keys:
            self._freq_keys[freq].pop(key, None)
            if not self._freq_keys[freq]:
                del self._freq_keys[freq]


# ===================================================================
# Cache (the orchestrator)
# ===================================================================

class Cache:
    """
    Key-value cache with configurable eviction policy and optional TTL.

    Key design decisions:
    1. Lazy expiration — expired entries are only removed when accessed
       via get(). This avoids background threads and keeps the design
       simple. Trade-off: stale entries consume memory until accessed.
    2. Clock injection — the clock parameter allows deterministic TTL
       testing without mocking time.time().
    3. Stats are tracked inline (no separate observer) for simplicity.
       In production you might emit events instead.
    """

    def __init__(
        self,
        capacity: int,
        eviction_policy: EvictionPolicy,
        clock: Callable[[], float] = time.time,
    ):
        self._capacity = capacity
        self._policy = eviction_policy
        self._clock = clock
        self._store: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value. Returns None on miss or expired entry."""
        entry = self._store.get(key)

        if entry is None:
            self._misses += 1
            return None

        # Lazy expiration
        if entry.is_expired(self._clock()):
            self._store.pop(key)
            self._policy.remove(key)
            self._misses += 1
            return None

        # Cache hit
        self._hits += 1
        now = self._clock()
        entry.access_count += 1
        entry.last_accessed = now
        self._policy.on_access(key)
        return entry.value

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Insert or update a key-value pair."""
        now = self._clock()

        # Update existing key
        if key in self._store:
            entry = self._store[key]
            entry.value = value
            entry.created_at = now
            entry.ttl = ttl
            entry.last_accessed = now
            entry.access_count += 1
            self._policy.on_access(key)
            return

        # Evict if at capacity
        if len(self._store) >= self._capacity:
            evicted_key = self._policy.evict()
            if evicted_key is not None:
                self._store.pop(evicted_key, None)
                self._evictions += 1

        # Insert new entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            ttl=ttl,
            access_count=0,
            last_accessed=now,
        )
        self._store[key] = entry
        self._policy.on_insert(key)

    def delete(self, key: str) -> bool:
        """Explicitly remove a key. Returns True if found."""
        if key not in self._store:
            return False
        self._store.pop(key)
        self._policy.remove(key)
        return True

    def clear(self) -> None:
        """Remove all entries."""
        for key in list(self._store.keys()):
            self._policy.remove(key)
        self._store.clear()

    def stats(self) -> CacheStats:
        """Return current cache statistics."""
        return CacheStats(
            hits=self._hits,
            misses=self._misses,
            evictions=self._evictions,
            current_size=len(self._store),
            capacity=self._capacity,
        )

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, key: str) -> bool:
        if key not in self._store:
            return False
        return not self._store[key].is_expired(self._clock())
