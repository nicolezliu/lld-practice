"""
Test driver for the Cache system.

Run this to verify your implementation:
    python main.py

Start with the basic scenarios, then add your own edge cases.
"""

from models import CacheEntry, CacheStats
from eviction import LRUPolicy, LFUPolicy
from cache import Cache
import time


def main():
    print("=" * 60)
    print("CACHE SYSTEM — LLD PRACTICE")
    print("=" * 60)

    # --- Scenario 1: LRU Cache ---
    print("\n--- Scenario 1: LRU Cache (capacity=3) ---")
    lru_cache = Cache(capacity=3, eviction_policy=LRUPolicy())

    lru_cache.put("a", "apple")
    lru_cache.put("b", "banana")
    lru_cache.put("c", "cherry")
    print(f"  get('a') = {lru_cache.get('a')}")  # hit
    print(f"  get('b') = {lru_cache.get('b')}")  # hit

    # Insert "d" — should evict "c" (least recently used)
    lru_cache.put("d", "date")
    print(f"  After inserting 'd' (evicts 'c'):")
    print(f"    get('c') = {lru_cache.get('c')}")  # miss (evicted)
    print(f"    get('a') = {lru_cache.get('a')}")  # hit
    print(f"    get('d') = {lru_cache.get('d')}")  # hit
    print(f"  Stats: {lru_cache.stats()}")

    # --- Scenario 2: LFU Cache ---
    print("\n--- Scenario 2: LFU Cache (capacity=3) ---")
    lfu_cache = Cache(capacity=3, eviction_policy=LFUPolicy())

    lfu_cache.put("x", 10)
    lfu_cache.put("y", 20)
    lfu_cache.put("z", 30)

    # Access "x" and "z" multiple times to increase their frequency
    lfu_cache.get("x")  # x: 2 accesses
    lfu_cache.get("x")  # x: 3 accesses
    lfu_cache.get("z")  # z: 2 accesses

    # Insert "w" — should evict "y" (least frequently used, freq=1)
    lfu_cache.put("w", 40)
    print(f"  After inserting 'w' (evicts 'y' — least frequent):")
    print(f"    get('y') = {lfu_cache.get('y')}")  # miss (evicted)
    print(f"    get('x') = {lfu_cache.get('x')}")  # hit
    print(f"    get('z') = {lfu_cache.get('z')}")  # hit
    print(f"    get('w') = {lfu_cache.get('w')}")  # hit
    print(f"  Stats: {lfu_cache.stats()}")

    # --- Scenario 3: TTL Expiry ---
    print("\n--- Scenario 3: TTL Expiry ---")
    ttl_cache = Cache(capacity=5, eviction_policy=LRUPolicy())

    ttl_cache.put("temp", "I expire soon!", ttl=1.0)
    print(f"  Immediately: get('temp') = {ttl_cache.get('temp')}")

    print("  Sleeping 1.5 seconds...")
    time.sleep(1.5)

    print(f"  After sleep:  get('temp') = {ttl_cache.get('temp')}")  # expired
    print(f"  Stats: {ttl_cache.stats()}")

    # --- Scenario 4: Cache stats and operations ---
    print("\n--- Scenario 4: Delete, Clear, and Stats ---")
    cache = Cache(capacity=5, eviction_policy=LRUPolicy())

    cache.put("1", "one")
    cache.put("2", "two")
    cache.put("3", "three")
    print(f"  Size: {len(cache)}")

    cache.delete("2")
    print(f"  After deleting '2': size={len(cache)}, get('2')={cache.get('2')}")

    cache.clear()
    print(f"  After clear: size={len(cache)}")
    print(f"  Stats: {cache.stats()}")

    # --- Scenario 5: Eviction comparison ---
    print("\n--- Scenario 5: LRU vs LFU Eviction Comparison ---")
    print("  Same access pattern, different eviction results:")

    for name, policy in [("LRU", LRUPolicy()), ("LFU", LFUPolicy())]:
        c = Cache(capacity=3, eviction_policy=policy)
        c.put("a", 1)
        c.put("b", 2)
        c.put("c", 3)
        c.get("a")  # access "a" once more
        c.get("a")  # access "a" again
        c.get("b")  # access "b" once more
        c.put("d", 4)  # triggers eviction
        evicted = [k for k in ["a", "b", "c"] if c.get(k) is None]
        print(f"  {name}: evicted {evicted}")

    # --- Add your own scenarios below! ---
    # Ideas:
    #   - What happens when you update an existing key's TTL?
    #   - What happens when all entries have TTL and they all expire?
    #   - Compare hit ratios between LRU and LFU for different access patterns
    #   - Try a Zipfian access pattern (some keys much more popular)


if __name__ == "__main__":
    main()
