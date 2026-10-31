# Cache System (LRU/LFU) — LLD Practice

## Problem Statement
Design a cache system supporting LRU (Least Recently Used) and LFU (Least
Frequently Used) eviction policies with O(1) get and put operations.

> **Note:** This is the most algorithmically challenging problem in the series.
> LFU with O(1) operations requires doubly-linked lists and frequency buckets —
> take your time with the data structure design before writing code.

## Requirements

### Functional
- `get(key)` — return the cached value, or `None` if not present
- `put(key, value, ttl=None)` — insert or update a key-value pair
- Configurable capacity — evict when full according to the active policy
- Support TTL (time-to-live) — entries expire after a specified duration
- Cache stats — track hits, misses, and eviction counts
- `delete(key)` — manually remove a key
- `clear()` — remove all entries

### Non-Functional
- O(1) time complexity for both `get` and `put` under LRU and LFU
- Swappable eviction policy without modifying the Cache class
- Deterministic testing — injectable clock for TTL tests

## Suggested Design Patterns
- **Strategy** — for the eviction policy (LRU, LFU, etc.)
- **Template Method** — common cache operations (stats tracking, TTL checks)
  with policy-specific eviction
- **Observer** — for eviction events (stretch goal)

## Your Task
1. Define the data models in `models.py` (CacheEntry, CacheStats)
2. Implement eviction policies in `eviction.py` (LRUPolicy, LFUPolicy)
3. Wire it all together in `cache.py` (the Cache orchestrator)
4. Run `main.py` to test your design end-to-end
5. Try swapping LRU for LFU and observe different eviction behavior

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models — CacheEntry, CacheStats
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: Eviction policies — LRU and LFU in isolation
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: Cache integration (TTL, stats, both policies)
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Add a distributed cache layer (consistent hashing for key partitioning)
- Implement write-through and write-back strategies
- Add an Observer that gets notified on eviction events
- Add a size-based eviction policy (evict largest entries first)
- Implement cache warming / pre-loading
