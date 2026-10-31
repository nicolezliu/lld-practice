"""
Eviction policies for the Cache system.

Your job: implement the Strategy pattern here.
- Define an abstract EvictionPolicy
- Implement LRUPolicy (Least Recently Used)
- Implement LFUPolicy (Least Frequently Used)

Think about:
- What data structures give you O(1) for all operations?
- For LRU: OrderedDict is your friend — moving to end is O(1)
- For LFU: you need a frequency map + a way to find the min-frequency key in O(1)
  Hint: maintain a dict of {frequency: set_of_keys} and track the current min frequency
"""

from abc import ABC, abstractmethod
from typing import Optional
from collections import OrderedDict


class EvictionPolicy(ABC):
    """
    Abstract eviction policy — decides which key to evict when the cache is full.

    The cache calls these hooks during its operations:
    - on_access(key): called when a key is read (get) or updated (put existing key)
    - on_insert(key): called when a new key is inserted
    - evict() -> key: called when the cache needs to free space — returns the key to remove
    - remove(key): called when a key is explicitly deleted from the cache
    """

    @abstractmethod
    def on_access(self, key: str) -> None:
        """Update internal state when a key is accessed (get or update)."""
        ...

    @abstractmethod
    def on_insert(self, key: str) -> None:
        """Update internal state when a new key is inserted."""
        ...

    @abstractmethod
    def evict(self) -> Optional[str]:
        """
        Select and remove the key to evict.

        Returns:
            The key to evict, or None if there are no keys to evict.
        """
        ...

    @abstractmethod
    def remove(self, key: str) -> None:
        """Remove a key from the policy's internal tracking."""
        ...


class LRUPolicy(EvictionPolicy):
    """
    Least Recently Used — evicts the key that hasn't been accessed for the longest time.

    Think about:
    - OrderedDict.move_to_end(key) is O(1)
    - OrderedDict.popitem(last=False) gives you the oldest item in O(1)
    - on_access → move to end
    - on_insert → add to end
    - evict → pop from front
    """

    def __init__(self):
        # TODO: initialize an OrderedDict to track access order
        pass

    def on_access(self, key: str) -> None:
        # TODO: move key to the end (most recently used)
        pass

    def on_insert(self, key: str) -> None:
        # TODO: add key to the end
        pass

    def evict(self) -> Optional[str]:
        # TODO: pop and return the least recently used key (front of OrderedDict)
        pass

    def remove(self, key: str) -> None:
        # TODO: remove the key from tracking
        pass


class LFUPolicy(EvictionPolicy):
    """
    Least Frequently Used — evicts the key with the fewest accesses.
    Ties are broken by least recently used (oldest insertion/access among min-freq keys).

    This is the hardest part of the problem. For O(1) you need:
    - key_freq: dict mapping key → current frequency
    - freq_keys: dict mapping frequency → OrderedDict of keys (preserves insertion order for tie-breaking)
    - min_freq: int tracking the current minimum frequency

    Think about:
    - on_insert: new key gets freq=1, update min_freq=1
    - on_access: move key from freq bucket to freq+1 bucket, update min_freq if needed
    - evict: pop the oldest key from freq_keys[min_freq]
    """

    def __init__(self):
        # TODO: initialize key_freq, freq_keys, and min_freq
        pass

    def on_access(self, key: str) -> None:
        # TODO:
        # 1. Get current frequency of the key
        # 2. Remove key from current frequency bucket
        # 3. If current frequency bucket is empty and it was min_freq, increment min_freq
        # 4. Add key to freq+1 bucket
        # 5. Update key_freq
        pass

    def on_insert(self, key: str) -> None:
        # TODO:
        # 1. Set key frequency to 1
        # 2. Add key to frequency-1 bucket
        # 3. Set min_freq to 1 (a new key always has the lowest frequency)
        pass

    def evict(self) -> Optional[str]:
        # TODO:
        # 1. Get the frequency bucket for min_freq
        # 2. Pop the oldest key from that bucket (FIFO for tie-breaking)
        # 3. Remove from key_freq
        # 4. Return the evicted key
        pass

    def remove(self, key: str) -> None:
        # TODO:
        # 1. Get the key's current frequency
        # 2. Remove from frequency bucket
        # 3. Remove from key_freq
        # 4. If the bucket is now empty and freq was min_freq, adjust min_freq
        pass
