"""
SOLUTION — Rate Limiter System

Don't peek until you've given it a solid attempt!

This is one valid solution. Yours may differ in structure and still be
perfectly correct — there's no single "right" LLD answer. Compare your
design choices against this one and think about trade-offs.

Design decisions in this solution:

1. Strategy pattern — each algorithm is a concrete RateLimiter subclass.
   The RateLimiterService is parameterized by the algorithm class.

2. Controllable clock — all algorithms accept a `clock` callable so tests
   can advance time deterministically without sleeping.

3. Lazy token refill (Token Bucket) — tokens are calculated on each call
   based on elapsed time, not via a background thread.

4. Per-client state — each algorithm stores state keyed by client_id in
   a dict. This makes client isolation trivial.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Optional


# ===================================================================
# Models
# ===================================================================

@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: Optional[float]
    limit: int


@dataclass
class RateLimitConfig:
    max_requests: int
    window_seconds: float


# ===================================================================
# Abstract base class
# ===================================================================

class RateLimiter(ABC):
    def __init__(self, config: RateLimitConfig, clock: Callable[[], float] = time.time):
        self._config = config
        self._clock = clock

    @abstractmethod
    def allow(self, client_id: str) -> RateLimitResult:
        ...

    @abstractmethod
    def reset(self, client_id: str) -> None:
        ...


# ===================================================================
# Token Bucket
# ===================================================================

class TokenBucketLimiter(RateLimiter):
    """
    Key design decisions:

    1. Tokens are floats internally so partial refills accumulate
       correctly. The "remaining" count returned to callers is
       truncated to int.

    2. Refill rate = max_requests / window_seconds. This means a
       full bucket refills in exactly one window duration.

    3. On each allow() call we calculate how many tokens to add
       based on (now - last_refill_time) * refill_rate. This avoids
       needing a background timer thread.
    """

    def __init__(self, config: RateLimitConfig, clock: Callable[[], float] = time.time):
        super().__init__(config, clock)
        # Per-client state: {client_id: [tokens (float), last_refill_time]}
        self._buckets: dict[str, list[float]] = {}

    def _get_or_create(self, client_id: str) -> list[float]:
        if client_id not in self._buckets:
            now = self._clock()
            self._buckets[client_id] = [float(self._config.max_requests), now]
        return self._buckets[client_id]

    def allow(self, client_id: str) -> RateLimitResult:
        bucket = self._get_or_create(client_id)
        now = self._clock()

        # Refill tokens based on elapsed time
        elapsed = now - bucket[1]
        refill_rate = self._config.max_requests / self._config.window_seconds
        bucket[0] = min(
            self._config.max_requests,
            bucket[0] + elapsed * refill_rate,
        )
        bucket[1] = now

        if bucket[0] >= 1.0:
            bucket[0] -= 1.0
            return RateLimitResult(
                allowed=True,
                remaining=int(bucket[0]),
                retry_after=None,
                limit=self._config.max_requests,
            )
        else:
            # How long until 1 token is available?
            tokens_needed = 1.0 - bucket[0]
            retry_after = tokens_needed / refill_rate
            return RateLimitResult(
                allowed=False,
                remaining=0,
                retry_after=retry_after,
                limit=self._config.max_requests,
            )

    def reset(self, client_id: str) -> None:
        self._buckets.pop(client_id, None)


# ===================================================================
# Fixed Window
# ===================================================================

class FixedWindowLimiter(RateLimiter):
    """
    Key design decisions:

    1. The window ID is computed as int(now // window_seconds). When
       the window ID changes, the counter resets.

    2. retry_after = (window_id + 1) * window_seconds - now, which
       is the time remaining in the current window.

    3. This algorithm can theoretically allow 2x burst at the boundary
       of two windows. That's a known trade-off vs simplicity.
    """

    def __init__(self, config: RateLimitConfig, clock: Callable[[], float] = time.time):
        super().__init__(config, clock)
        # Per-client state: {client_id: [window_id, count]}
        self._windows: dict[str, list] = {}

    def allow(self, client_id: str) -> RateLimitResult:
        now = self._clock()
        window_id = int(now // self._config.window_seconds)

        if client_id not in self._windows or self._windows[client_id][0] != window_id:
            self._windows[client_id] = [window_id, 0]

        state = self._windows[client_id]

        if state[1] < self._config.max_requests:
            state[1] += 1
            remaining = self._config.max_requests - state[1]
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                retry_after=None,
                limit=self._config.max_requests,
            )
        else:
            # Time until next window
            window_end = (window_id + 1) * self._config.window_seconds
            retry_after = window_end - now
            return RateLimitResult(
                allowed=False,
                remaining=0,
                retry_after=retry_after,
                limit=self._config.max_requests,
            )

    def reset(self, client_id: str) -> None:
        self._windows.pop(client_id, None)


# ===================================================================
# Sliding Window Log
# ===================================================================

class SlidingWindowLogLimiter(RateLimiter):
    """
    Key design decisions:

    1. Each client's log is a list of timestamps in chronological order.
       Old entries are pruned on each allow() call.

    2. Memory usage scales with request rate — high-traffic clients
       accumulate more timestamps. In production you'd want a TTL or
       periodic cleanup.

    3. retry_after is based on when the oldest entry in the window
       will expire: oldest_timestamp + window_seconds - now.
    """

    def __init__(self, config: RateLimitConfig, clock: Callable[[], float] = time.time):
        super().__init__(config, clock)
        # Per-client state: {client_id: [list of timestamps]}
        self._logs: dict[str, list[float]] = {}

    def allow(self, client_id: str) -> RateLimitResult:
        now = self._clock()
        if client_id not in self._logs:
            self._logs[client_id] = []

        log = self._logs[client_id]

        # Remove expired entries
        cutoff = now - self._config.window_seconds
        while log and log[0] <= cutoff:
            log.pop(0)

        if len(log) < self._config.max_requests:
            log.append(now)
            remaining = self._config.max_requests - len(log)
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                retry_after=None,
                limit=self._config.max_requests,
            )
        else:
            # Retry after the oldest entry expires
            retry_after = log[0] + self._config.window_seconds - now
            return RateLimitResult(
                allowed=False,
                remaining=0,
                retry_after=retry_after,
                limit=self._config.max_requests,
            )

    def reset(self, client_id: str) -> None:
        self._logs.pop(client_id, None)


# ===================================================================
# RateLimiterService (the orchestrator)
# ===================================================================

class RateLimiterService:
    """
    Key design decisions:

    1. The service is parameterized by algorithm_class (a RateLimiter
       subclass). This is the Strategy pattern — swap the algorithm
       without changing the service.

    2. Per-client limiters are stored in a dict. When set_limit is
       called, a new limiter replaces the old one (fresh state).

    3. Default limiters are created lazily for unknown clients.
       If no default_config is set, unknown clients are always allowed.

    4. Thread safety is NOT implemented here. In production you'd
       wrap allow_request / set_limit with a threading.Lock.
    """

    def __init__(
        self,
        algorithm_class: type[RateLimiter] = TokenBucketLimiter,
        default_config: Optional[RateLimitConfig] = None,
        clock: Callable[[], float] = time.time,
    ):
        self._algorithm_class = algorithm_class
        self._default_config = default_config
        self._clock = clock
        self._client_limiters: dict[str, RateLimiter] = {}
        self._default_limiters: dict[str, RateLimiter] = {}

    def set_limit(self, client_id: str, config: RateLimitConfig) -> None:
        self._client_limiters[client_id] = self._algorithm_class(config, clock=self._clock)
        # Remove any default limiter for this client
        self._default_limiters.pop(client_id, None)

    def remove_limit(self, client_id: str) -> None:
        self._client_limiters.pop(client_id, None)
        # Also clear any cached default limiter so it starts fresh
        self._default_limiters.pop(client_id, None)

    def allow_request(self, client_id: str) -> RateLimitResult:
        # 1. Check for client-specific limiter
        if client_id in self._client_limiters:
            return self._client_limiters[client_id].allow(client_id)

        # 2. Use default limiter if config is set
        if self._default_config is not None:
            if client_id not in self._default_limiters:
                self._default_limiters[client_id] = self._algorithm_class(
                    self._default_config, clock=self._clock
                )
            return self._default_limiters[client_id].allow(client_id)

        # 3. No limits configured — allow everything
        return RateLimitResult(
            allowed=True,
            remaining=999999,
            retry_after=None,
            limit=0,
        )

    def get_client_status(self, client_id: str) -> dict:
        if client_id in self._client_limiters:
            return {
                "has_custom_limit": True,
                "config": self._client_limiters[client_id]._config,
            }
        return {
            "has_custom_limit": False,
            "config": self._default_config,
        }

    def set_default_limit(self, config: RateLimitConfig) -> None:
        self._default_config = config
        # Clear cached default limiters so they pick up the new config
        self._default_limiters.clear()
