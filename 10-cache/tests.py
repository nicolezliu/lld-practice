"""
Phased tests for the Cache system.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models only
    python -m pytest tests.py -v -k "phase2"    # Eviction policies only
    python -m pytest tests.py -v -k "phase3"    # Cache integration

Each phase builds on the previous — start with phase1 and get all tests
green before moving on.
"""

import pytest

from models import CacheEntry, CacheStats
from eviction import LRUPolicy, LFUPolicy
from cache import Cache


# ===================================================================
# PHASE 1: Models — CacheEntry, CacheStats
# ===================================================================

class TestPhase1CacheEntry:
    """Verify CacheEntry data and expiry logic."""

    def test_entry_stores_key_and_value(self):
        entry = CacheEntry(key="a", value=1, created_at=100.0)
        assert entry.key == "a"
        assert entry.value == 1

    def test_entry_default_access_count(self):
        entry = CacheEntry(key="a", value=1, created_at=100.0)
        assert entry.access_count == 0

    def test_entry_default_ttl_is_none(self):
        entry = CacheEntry(key="a", value=1, created_at=100.0)
        assert entry.ttl is None

    def test_entry_no_ttl_never_expires(self):
        entry = CacheEntry(key="a", value=1, created_at=100.0, ttl=None)
        assert entry.is_expired(current_time=999999.0) is False

    def test_entry_not_expired_within_ttl(self):
        entry = CacheEntry(key="a", value=1, created_at=100.0, ttl=10.0)
        assert entry.is_expired(current_time=105.0) is False

    def test_entry_expired_after_ttl(self):
        entry = CacheEntry(key="a", value=1, created_at=100.0, ttl=10.0)
        assert entry.is_expired(current_time=111.0) is True

    def test_entry_expired_exactly_at_ttl(self):
        entry = CacheEntry(key="a", value=1, created_at=100.0, ttl=10.0)
        # At exactly created_at + ttl, the entry should be expired
        assert entry.is_expired(current_time=110.0) is True

    def test_entry_last_accessed(self):
        entry = CacheEntry(key="a", value=1, created_at=100.0, last_accessed=100.0)
        assert entry.last_accessed == 100.0


class TestPhase1CacheStats:
    """Verify CacheStats tracking and computed properties."""

    def test_default_stats(self):
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0

    def test_stats_with_values(self):
        stats = CacheStats(hits=10, misses=5, evictions=2, current_size=8, capacity=10)
        assert stats.hits == 10
        assert stats.misses == 5
        assert stats.evictions == 2
        assert stats.current_size == 8
        assert stats.capacity == 10

    def test_hit_ratio_no_requests(self):
        stats = CacheStats()
        assert stats.hit_ratio == 0.0

    def test_hit_ratio_all_hits(self):
        stats = CacheStats(hits=10, misses=0)
        assert stats.hit_ratio == 1.0

    def test_hit_ratio_mixed(self):
        stats = CacheStats(hits=3, misses=7)
        assert stats.hit_ratio == pytest.approx(0.3)

    def test_hit_ratio_all_misses(self):
        stats = CacheStats(hits=0, misses=10)
        assert stats.hit_ratio == 0.0

    def test_stats_size_and_capacity(self):
        stats = CacheStats(current_size=5, capacity=10)
        assert stats.current_size == 5
        assert stats.capacity == 10


# ===================================================================
# PHASE 2: Eviction Policies — LRU and LFU in isolation
# ===================================================================

class TestPhase2LRUInsertAndEvict:
    """Verify LRU insert ordering and eviction."""

    def test_evict_returns_first_inserted(self):
        policy = LRUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        assert policy.evict() == "a"

    def test_evict_order_is_fifo_without_access(self):
        policy = LRUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        assert policy.evict() == "a"
        assert policy.evict() == "b"
        assert policy.evict() == "c"

    def test_evict_empty_returns_none(self):
        policy = LRUPolicy()
        assert policy.evict() is None

    def test_single_insert_evict(self):
        policy = LRUPolicy()
        policy.on_insert("x")
        assert policy.evict() == "x"
        assert policy.evict() is None


class TestPhase2LRUAccessReordering:
    """Verify LRU reordering on access."""

    def test_access_moves_to_back(self):
        policy = LRUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        policy.on_access("a")  # "a" is now most recently used
        assert policy.evict() == "b"  # "b" is now LRU

    def test_multiple_accesses_reorder(self):
        policy = LRUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        policy.on_access("a")
        policy.on_access("b")
        # Order is now: c, a, b — "c" is LRU
        assert policy.evict() == "c"
        assert policy.evict() == "a"
        assert policy.evict() == "b"

    def test_access_same_key_repeatedly(self):
        policy = LRUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_access("a")
        policy.on_access("a")
        policy.on_access("a")
        assert policy.evict() == "b"  # "b" is still LRU


class TestPhase2LRURemove:
    """Verify LRU explicit removal."""

    def test_remove_key(self):
        policy = LRUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        policy.remove("b")
        assert policy.evict() == "a"
        assert policy.evict() == "c"

    def test_remove_nonexistent_key_no_error(self):
        policy = LRUPolicy()
        policy.on_insert("a")
        policy.remove("z")  # should not raise
        assert policy.evict() == "a"


class TestPhase2LFUInsertAndEvict:
    """Verify LFU eviction by frequency."""

    def test_evict_least_frequent(self):
        policy = LFUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        policy.on_access("b")  # b: freq 2
        policy.on_access("c")  # c: freq 2
        # "a" still has freq 1 → should be evicted first
        assert policy.evict() == "a"

    def test_evict_all_same_frequency_uses_insertion_order(self):
        """When all keys have the same frequency, evict the oldest (FIFO)."""
        policy = LFUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        # All have freq=1, "a" was inserted first
        assert policy.evict() == "a"

    def test_evict_empty_returns_none(self):
        policy = LFUPolicy()
        assert policy.evict() is None

    def test_single_insert_evict(self):
        policy = LFUPolicy()
        policy.on_insert("x")
        assert policy.evict() == "x"
        assert policy.evict() is None


class TestPhase2LFUAccessAndFrequency:
    """Verify LFU frequency tracking and tie-breaking."""

    def test_access_increases_frequency(self):
        policy = LFUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_access("a")  # a: freq 2
        policy.on_access("a")  # a: freq 3
        # "b" has lower frequency → evicted first
        assert policy.evict() == "b"

    def test_tie_breaking_by_recency(self):
        """Among keys with the same frequency, evict the least recently inserted/accessed."""
        policy = LFUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        # All have freq=1; access "a" to move it to freq=2
        # Then access both "b" and "c" once → both at freq=2
        policy.on_access("a")  # a: freq 2
        policy.on_access("b")  # b: freq 2
        policy.on_access("c")  # c: freq 2
        # All at freq=2 — "a" was accessed first among freq-2 keys → evict "a"
        assert policy.evict() == "a"

    def test_new_insert_resets_min_freq(self):
        policy = LFUPolicy()
        policy.on_insert("a")
        policy.on_access("a")  # a: freq 2
        policy.on_access("a")  # a: freq 3
        policy.on_insert("b")  # b: freq 1, new min_freq = 1
        assert policy.evict() == "b"  # b has lowest freq

    def test_mixed_frequencies(self):
        policy = LFUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        policy.on_access("c")  # c: freq 2
        policy.on_access("c")  # c: freq 3
        policy.on_access("b")  # b: freq 2
        # Frequencies: a=1, b=2, c=3
        assert policy.evict() == "a"  # lowest freq
        assert policy.evict() == "b"  # next lowest
        assert policy.evict() == "c"  # highest freq, last remaining


class TestPhase2LFURemove:
    """Verify LFU explicit removal."""

    def test_remove_key(self):
        policy = LFUPolicy()
        policy.on_insert("a")
        policy.on_insert("b")
        policy.on_insert("c")
        policy.remove("a")
        # "b" is now the least frequent (b and c both freq=1, b is older)
        assert policy.evict() == "b"

    def test_remove_nonexistent_key_no_error(self):
        policy = LFUPolicy()
        policy.on_insert("a")
        policy.remove("z")  # should not raise
        assert policy.evict() == "a"


# ===================================================================
# PHASE 3: Cache Integration — TTL, Stats, Both Policies
# ===================================================================

class TestPhase3CacheLRUBasic:
    """Basic cache operations with LRU policy."""

    def test_put_and_get(self):
        cache = Cache(capacity=3, eviction_policy=LRUPolicy())
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_get_missing_key_returns_none(self):
        cache = Cache(capacity=3, eviction_policy=LRUPolicy())
        assert cache.get("missing") is None

    def test_put_updates_existing_key(self):
        cache = Cache(capacity=3, eviction_policy=LRUPolicy())
        cache.put("a", 1)
        cache.put("a", 2)
        assert cache.get("a") == 2

    def test_eviction_when_full(self):
        cache = Cache(capacity=2, eviction_policy=LRUPolicy())
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # should evict "a"
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_lru_eviction_respects_access_order(self):
        cache = Cache(capacity=2, eviction_policy=LRUPolicy())
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")  # "a" is now most recently used
        cache.put("c", 3)  # should evict "b" (LRU)
        assert cache.get("b") is None
        assert cache.get("a") == 1
        assert cache.get("c") == 3


class TestPhase3CacheLFUBasic:
    """Basic cache operations with LFU policy."""

    def test_lfu_eviction_by_frequency(self):
        cache = Cache(capacity=2, eviction_policy=LFUPolicy())
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")  # "a" accessed twice (put + get)
        cache.put("c", 3)  # should evict "b" (least frequently used)
        assert cache.get("b") is None
        assert cache.get("a") == 1

    def test_lfu_eviction_tie_breaking(self):
        cache = Cache(capacity=2, eviction_policy=LFUPolicy())
        cache.put("a", 1)
        cache.put("b", 2)
        # Both have same frequency — "a" was inserted first
        cache.put("c", 3)  # should evict "a" (oldest with min freq)
        assert cache.get("a") is None
        assert cache.get("b") == 2


class TestPhase3CacheTTL:
    """Cache TTL (time-to-live) expiry tests with injected clock."""

    def test_entry_accessible_before_ttl(self):
        fake_time = [100.0]
        cache = Cache(capacity=3, eviction_policy=LRUPolicy(), clock=lambda: fake_time[0])
        cache.put("a", 1, ttl=10.0)
        fake_time[0] = 105.0  # 5 seconds later, within TTL
        assert cache.get("a") == 1

    def test_entry_expired_after_ttl(self):
        fake_time = [100.0]
        cache = Cache(capacity=3, eviction_policy=LRUPolicy(), clock=lambda: fake_time[0])
        cache.put("a", 1, ttl=10.0)
        fake_time[0] = 111.0  # 11 seconds later, past TTL
        assert cache.get("a") is None

    def test_no_ttl_never_expires(self):
        fake_time = [100.0]
        cache = Cache(capacity=3, eviction_policy=LRUPolicy(), clock=lambda: fake_time[0])
        cache.put("a", 1)  # no TTL
        fake_time[0] = 999999.0
        assert cache.get("a") == 1

    def test_expired_entry_is_removed_from_cache(self):
        fake_time = [100.0]
        cache = Cache(capacity=3, eviction_policy=LRUPolicy(), clock=lambda: fake_time[0])
        cache.put("a", 1, ttl=5.0)
        fake_time[0] = 106.0
        cache.get("a")  # triggers lazy expiration
        assert len(cache) == 0


class TestPhase3CacheStats:
    """Cache statistics tracking."""

    def test_hit_tracking(self):
        cache = Cache(capacity=3, eviction_policy=LRUPolicy())
        cache.put("a", 1)
        cache.get("a")
        s = cache.stats()
        assert s.hits == 1

    def test_miss_tracking(self):
        cache = Cache(capacity=3, eviction_policy=LRUPolicy())
        cache.get("missing")
        s = cache.stats()
        assert s.misses == 1

    def test_eviction_tracking(self):
        cache = Cache(capacity=2, eviction_policy=LRUPolicy())
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # evicts "a"
        s = cache.stats()
        assert s.evictions == 1

    def test_stats_size_and_capacity(self):
        cache = Cache(capacity=5, eviction_policy=LRUPolicy())
        cache.put("a", 1)
        cache.put("b", 2)
        s = cache.stats()
        assert s.current_size == 2
        assert s.capacity == 5

    def test_expired_entry_counted_as_miss(self):
        fake_time = [100.0]
        cache = Cache(capacity=3, eviction_policy=LRUPolicy(), clock=lambda: fake_time[0])
        cache.put("a", 1, ttl=5.0)
        fake_time[0] = 106.0
        cache.get("a")  # expired → miss
        s = cache.stats()
        assert s.misses == 1
        assert s.hits == 0


class TestPhase3CacheDeleteAndClear:
    """Cache delete and clear operations."""

    def test_delete_existing_key(self):
        cache = Cache(capacity=3, eviction_policy=LRUPolicy())
        cache.put("a", 1)
        assert cache.delete("a") is True
        assert cache.get("a") is None

    def test_delete_nonexistent_key(self):
        cache = Cache(capacity=3, eviction_policy=LRUPolicy())
        assert cache.delete("missing") is False

    def test_clear_removes_all(self):
        cache = Cache(capacity=3, eviction_policy=LRUPolicy())
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        assert len(cache) == 0
        assert cache.get("a") is None
        assert cache.get("b") is None
