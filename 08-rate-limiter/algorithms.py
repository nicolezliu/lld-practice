"""
Rate-limiting algorithms.

Your job: implement the Strategy pattern for rate limiting.
- Define an abstract RateLimiter base class
- Implement three concrete algorithms: TokenBucket, FixedWindow, SlidingWindowLog
- Each algorithm tracks state per client_id

Think about trade-offs:
- Token Bucket is smooth and allows bursts up to the bucket size
- Fixed Window is simple but can allow 2x burst at window boundaries
- Sliding Window Log is precise but uses more memory (stores timestamps)

All algorithms accept an optional `clock` callable (defaults to time.time)
so that tests can control time without sleeping.
"""

import time
from abc import ABC, abstractmethod
from typing import Callable, Optional

from models import RateLimitResult, RateLimitConfig


class RateLimiter(ABC):
    """
    Abstract rate limiter — checks whether a request should be allowed.

    Think about:
    - What state does each algorithm need per client?
    - How does the clock parameter help with testing?
    - What does reset() need to clean up?
    """

    def __init__(self, config: RateLimitConfig, clock: Callable[[], float] = time.time):
        """
        Args:
            config: the rate-limit configuration (max requests, window size)
            clock: a callable that returns the current time in seconds
                   (defaults to time.time, override in tests)
        """
        # TODO: store config and clock
        pass

    @abstractmethod
    def allow(self, client_id: str) -> RateLimitResult:
        """
        Check if a request from the given client should be allowed.

        Returns:
            RateLimitResult with allowed/denied status, remaining quota, etc.
        """
        ...

    @abstractmethod
    def reset(self, client_id: str) -> None:
        """Reset the rate-limit state for a specific client."""
        ...


class TokenBucketLimiter(RateLimiter):
    """
    Token Bucket algorithm.

    How it works:
    - Each client has a "bucket" that holds up to max_requests tokens
    - Tokens refill at a steady rate: max_requests / window_seconds per second
    - Each request consumes one token
    - If the bucket is empty, the request is denied

    Think about:
    - How do you track tokens without a background thread?
      (Hint: calculate tokens lazily based on elapsed time)
    - What state do you need per client? (token count, last refill time)
    """

    def __init__(self, config: RateLimitConfig, clock: Callable[[], float] = time.time):
        # TODO: call super().__init__ and set up per-client state storage
        pass

    def allow(self, client_id: str) -> RateLimitResult:
        # TODO:
        # 1. If client is new, initialize their bucket to max_requests tokens
        # 2. Calculate tokens to add based on time elapsed since last check
        # 3. Cap tokens at max_requests
        # 4. If tokens >= 1, consume one and allow
        # 5. If tokens < 1, deny and calculate retry_after
        pass

    def reset(self, client_id: str) -> None:
        # TODO: remove client's state
        pass


class FixedWindowLimiter(RateLimiter):
    """
    Fixed Window algorithm.

    How it works:
    - Time is divided into fixed windows of window_seconds duration
    - Each client has a counter that tracks requests in the current window
    - When a new window starts, the counter resets to zero
    - If the counter exceeds max_requests, the request is denied

    Think about:
    - How do you determine which window the current time falls in?
      (Hint: integer division of timestamp by window_seconds)
    - What state do you need per client? (current window ID, request count)
    - What happens at the boundary between two windows?
    """

    def __init__(self, config: RateLimitConfig, clock: Callable[[], float] = time.time):
        # TODO: call super().__init__ and set up per-client state storage
        pass

    def allow(self, client_id: str) -> RateLimitResult:
        # TODO:
        # 1. Determine the current window (timestamp // window_seconds)
        # 2. If client is new or in a new window, reset their counter
        # 3. If counter < max_requests, increment and allow
        # 4. Otherwise, deny and calculate retry_after (time until next window)
        pass

    def reset(self, client_id: str) -> None:
        # TODO: remove client's state
        pass


class SlidingWindowLogLimiter(RateLimiter):
    """
    Sliding Window Log algorithm.

    How it works:
    - Each client keeps a log (list) of request timestamps
    - On each request, remove timestamps older than window_seconds
    - If the remaining count is under max_requests, allow and log the timestamp
    - Otherwise, deny

    Think about:
    - Memory usage: each request adds a timestamp to the log
    - How do you efficiently remove old entries? (they're in chronological order)
    - How do you calculate retry_after? (when will the oldest entry expire?)
    """

    def __init__(self, config: RateLimitConfig, clock: Callable[[], float] = time.time):
        # TODO: call super().__init__ and set up per-client state storage
        pass

    def allow(self, client_id: str) -> RateLimitResult:
        # TODO:
        # 1. Get (or create) the client's timestamp log
        # 2. Remove all timestamps older than (now - window_seconds)
        # 3. If len(log) < max_requests, append now and allow
        # 4. Otherwise, deny and calculate retry_after
        #    (retry_after = oldest_timestamp + window_seconds - now)
        pass

    def reset(self, client_id: str) -> None:
        # TODO: remove client's state
        pass
