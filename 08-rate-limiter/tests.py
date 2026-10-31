"""
Phased tests for the Rate Limiter system.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models only
    python -m pytest tests.py -v -k "phase2"    # Algorithms only
    python -m pytest tests.py -v -k "phase3"    # RateLimiterService integration

Each phase builds on the previous — start with phase1 and get all tests
green before moving on.
"""

import pytest

from models import RateLimitResult, RateLimitConfig
from algorithms import TokenBucketLimiter, FixedWindowLimiter, SlidingWindowLogLimiter
from rate_limiter import RateLimiterService


# ===================================================================
# PHASE 1: Models — RateLimitResult, RateLimitConfig
# ===================================================================

class TestPhase1RateLimitResult:
    """Verify RateLimitResult data class."""

    def test_allowed_result(self):
        result = RateLimitResult(allowed=True, remaining=9, retry_after=None, limit=10)
        assert result.allowed is True
        assert result.remaining == 9
        assert result.retry_after is None
        assert result.limit == 10

    def test_denied_result(self):
        result = RateLimitResult(allowed=False, remaining=0, retry_after=5.0, limit=10)
        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after == 5.0
        assert result.limit == 10

    def test_result_equality(self):
        r1 = RateLimitResult(allowed=True, remaining=5, retry_after=None, limit=10)
        r2 = RateLimitResult(allowed=True, remaining=5, retry_after=None, limit=10)
        assert r1 == r2

    def test_result_inequality(self):
        r1 = RateLimitResult(allowed=True, remaining=5, retry_after=None, limit=10)
        r2 = RateLimitResult(allowed=False, remaining=0, retry_after=1.0, limit=10)
        assert r1 != r2


class TestPhase1RateLimitConfig:
    """Verify RateLimitConfig data class."""

    def test_config_creation(self):
        config = RateLimitConfig(max_requests=100, window_seconds=60.0)
        assert config.max_requests == 100
        assert config.window_seconds == 60.0

    def test_config_equality(self):
        c1 = RateLimitConfig(max_requests=10, window_seconds=1.0)
        c2 = RateLimitConfig(max_requests=10, window_seconds=1.0)
        assert c1 == c2


# ===================================================================
# Controllable clock helper for phase 2 and 3
# ===================================================================

class FakeClock:
    """A controllable clock for deterministic testing."""

    def __init__(self, start: float = 1000.0):
        self._now = start

    def __call__(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds

    def set(self, time: float) -> None:
        self._now = time


# ===================================================================
# PHASE 2: Algorithms — TokenBucket, FixedWindow, SlidingWindowLog
# ===================================================================

class TestPhase2TokenBucket:
    """Verify Token Bucket rate-limiting algorithm."""

    def test_allow_within_limit(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=5, window_seconds=10.0)
        limiter = TokenBucketLimiter(config, clock=clock)

        result = limiter.allow("client-1")
        assert result.allowed is True
        assert result.remaining == 4
        assert result.limit == 5

    def test_allow_multiple_within_limit(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=5, window_seconds=10.0)
        limiter = TokenBucketLimiter(config, clock=clock)

        for i in range(5):
            result = limiter.allow("client-1")
            assert result.allowed is True
            assert result.remaining == 4 - i

    def test_deny_over_limit(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=3, window_seconds=10.0)
        limiter = TokenBucketLimiter(config, clock=clock)

        for _ in range(3):
            limiter.allow("client-1")

        result = limiter.allow("client-1")
        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after is not None
        assert result.retry_after > 0

    def test_tokens_refill_over_time(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=10, window_seconds=10.0)
        limiter = TokenBucketLimiter(config, clock=clock)

        # Use all tokens
        for _ in range(10):
            limiter.allow("client-1")

        result = limiter.allow("client-1")
        assert result.allowed is False

        # Advance time enough to refill 1 token (rate = 10/10 = 1 token/sec)
        clock.advance(1.0)
        result = limiter.allow("client-1")
        assert result.allowed is True

    def test_tokens_cap_at_max(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=5, window_seconds=10.0)
        limiter = TokenBucketLimiter(config, clock=clock)

        # Use 1 token
        limiter.allow("client-1")

        # Wait a very long time — tokens should cap at max_requests
        clock.advance(1000.0)
        result = limiter.allow("client-1")
        assert result.remaining == 4  # max is 5, used 1 = 4 remaining

    def test_independent_clients(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=2, window_seconds=10.0)
        limiter = TokenBucketLimiter(config, clock=clock)

        # Exhaust client-1
        limiter.allow("client-1")
        limiter.allow("client-1")
        result = limiter.allow("client-1")
        assert result.allowed is False

        # client-2 should still be allowed
        result = limiter.allow("client-2")
        assert result.allowed is True

    def test_reset_restores_tokens(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=3, window_seconds=10.0)
        limiter = TokenBucketLimiter(config, clock=clock)

        for _ in range(3):
            limiter.allow("client-1")

        result = limiter.allow("client-1")
        assert result.allowed is False

        limiter.reset("client-1")
        result = limiter.allow("client-1")
        assert result.allowed is True
        assert result.remaining == 2

    def test_retry_after_accuracy(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=2, window_seconds=10.0)
        limiter = TokenBucketLimiter(config, clock=clock)

        limiter.allow("client-1")
        limiter.allow("client-1")
        result = limiter.allow("client-1")
        assert result.allowed is False
        # refill rate = 2/10 = 0.2 tokens/sec, need 1 token → 5 seconds
        assert result.retry_after is not None
        assert abs(result.retry_after - 5.0) < 0.01


class TestPhase2FixedWindow:
    """Verify Fixed Window rate-limiting algorithm."""

    def test_allow_within_limit(self):
        clock = FakeClock(start=1000.0)
        config = RateLimitConfig(max_requests=5, window_seconds=10.0)
        limiter = FixedWindowLimiter(config, clock=clock)

        result = limiter.allow("client-1")
        assert result.allowed is True
        assert result.remaining == 4
        assert result.limit == 5

    def test_allow_multiple_within_limit(self):
        clock = FakeClock(start=1000.0)
        config = RateLimitConfig(max_requests=5, window_seconds=10.0)
        limiter = FixedWindowLimiter(config, clock=clock)

        for i in range(5):
            result = limiter.allow("client-1")
            assert result.allowed is True
            assert result.remaining == 4 - i

    def test_deny_over_limit(self):
        clock = FakeClock(start=1000.0)
        config = RateLimitConfig(max_requests=3, window_seconds=10.0)
        limiter = FixedWindowLimiter(config, clock=clock)

        for _ in range(3):
            limiter.allow("client-1")

        result = limiter.allow("client-1")
        assert result.allowed is False
        assert result.remaining == 0

    def test_window_resets_counter(self):
        clock = FakeClock(start=1000.0)
        config = RateLimitConfig(max_requests=3, window_seconds=10.0)
        limiter = FixedWindowLimiter(config, clock=clock)

        # Use all requests
        for _ in range(3):
            limiter.allow("client-1")

        result = limiter.allow("client-1")
        assert result.allowed is False

        # Advance to next window
        clock.advance(10.0)
        result = limiter.allow("client-1")
        assert result.allowed is True
        assert result.remaining == 2

    def test_retry_after_returns_window_remaining(self):
        clock = FakeClock(start=1000.0)
        config = RateLimitConfig(max_requests=2, window_seconds=10.0)
        limiter = FixedWindowLimiter(config, clock=clock)

        limiter.allow("client-1")
        limiter.allow("client-1")

        # 3 seconds into a 10-second window
        clock.advance(3.0)
        result = limiter.allow("client-1")
        assert result.allowed is False
        assert result.retry_after is not None
        # Window started at 1000, ends at 1010, now is 1003 → 7 seconds left
        assert abs(result.retry_after - 7.0) < 0.01

    def test_independent_clients(self):
        clock = FakeClock(start=1000.0)
        config = RateLimitConfig(max_requests=2, window_seconds=10.0)
        limiter = FixedWindowLimiter(config, clock=clock)

        limiter.allow("client-1")
        limiter.allow("client-1")
        result = limiter.allow("client-1")
        assert result.allowed is False

        result = limiter.allow("client-2")
        assert result.allowed is True

    def test_reset_clears_counter(self):
        clock = FakeClock(start=1000.0)
        config = RateLimitConfig(max_requests=2, window_seconds=10.0)
        limiter = FixedWindowLimiter(config, clock=clock)

        limiter.allow("client-1")
        limiter.allow("client-1")
        result = limiter.allow("client-1")
        assert result.allowed is False

        limiter.reset("client-1")
        result = limiter.allow("client-1")
        assert result.allowed is True


class TestPhase2SlidingWindowLog:
    """Verify Sliding Window Log rate-limiting algorithm."""

    def test_allow_within_limit(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=5, window_seconds=10.0)
        limiter = SlidingWindowLogLimiter(config, clock=clock)

        result = limiter.allow("client-1")
        assert result.allowed is True
        assert result.remaining == 4
        assert result.limit == 5

    def test_allow_multiple_within_limit(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=5, window_seconds=10.0)
        limiter = SlidingWindowLogLimiter(config, clock=clock)

        for i in range(5):
            result = limiter.allow("client-1")
            assert result.allowed is True
            assert result.remaining == 4 - i

    def test_deny_over_limit(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=3, window_seconds=10.0)
        limiter = SlidingWindowLogLimiter(config, clock=clock)

        for _ in range(3):
            limiter.allow("client-1")

        result = limiter.allow("client-1")
        assert result.allowed is False
        assert result.remaining == 0

    def test_old_requests_expire(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=3, window_seconds=10.0)
        limiter = SlidingWindowLogLimiter(config, clock=clock)

        # Make 3 requests at time 1000
        for _ in range(3):
            limiter.allow("client-1")

        result = limiter.allow("client-1")
        assert result.allowed is False

        # Advance past the window — all 3 requests should expire
        clock.advance(10.01)
        result = limiter.allow("client-1")
        assert result.allowed is True
        assert result.remaining == 2

    def test_partial_expiry(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=3, window_seconds=10.0)
        limiter = SlidingWindowLogLimiter(config, clock=clock)

        # Request at t=1000
        limiter.allow("client-1")
        # Request at t=1005
        clock.advance(5.0)
        limiter.allow("client-1")
        # Request at t=1007
        clock.advance(2.0)
        limiter.allow("client-1")

        # At t=1007, all 3 are in the window, should deny
        result = limiter.allow("client-1")
        assert result.allowed is False

        # Advance to t=1010.01 — first request (t=1000) expires
        clock.advance(3.01)
        result = limiter.allow("client-1")
        assert result.allowed is True

    def test_retry_after_based_on_oldest(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=2, window_seconds=10.0)
        limiter = SlidingWindowLogLimiter(config, clock=clock)

        # 2 requests at t=1000
        limiter.allow("client-1")
        limiter.allow("client-1")

        # At t=1003, denied — oldest expires at t=1010
        clock.advance(3.0)
        result = limiter.allow("client-1")
        assert result.allowed is False
        assert result.retry_after is not None
        # Oldest timestamp is 1000, expires at 1010, now is 1003 → retry_after ≈ 7.0
        assert abs(result.retry_after - 7.0) < 0.01

    def test_independent_clients(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=2, window_seconds=10.0)
        limiter = SlidingWindowLogLimiter(config, clock=clock)

        limiter.allow("client-1")
        limiter.allow("client-1")
        result = limiter.allow("client-1")
        assert result.allowed is False

        result = limiter.allow("client-2")
        assert result.allowed is True

    def test_reset_clears_log(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=2, window_seconds=10.0)
        limiter = SlidingWindowLogLimiter(config, clock=clock)

        limiter.allow("client-1")
        limiter.allow("client-1")
        result = limiter.allow("client-1")
        assert result.allowed is False

        limiter.reset("client-1")
        result = limiter.allow("client-1")
        assert result.allowed is True
        assert result.remaining == 1


# ===================================================================
# PHASE 3: RateLimiterService Integration
# ===================================================================

class TestPhase3RateLimiterService:
    """Full integration tests for the RateLimiterService."""

    def test_default_config_limits_unknown_clients(self):
        clock = FakeClock()
        default = RateLimitConfig(max_requests=3, window_seconds=10.0)
        service = RateLimiterService(
            algorithm_class=TokenBucketLimiter,
            default_config=default,
            clock=clock,
        )

        for _ in range(3):
            result = service.allow_request("unknown-client")
            assert result.allowed is True

        result = service.allow_request("unknown-client")
        assert result.allowed is False

    def test_no_default_allows_all(self):
        clock = FakeClock()
        service = RateLimiterService(
            algorithm_class=TokenBucketLimiter,
            default_config=None,
            clock=clock,
        )

        # Without a default config, all requests should be allowed
        for _ in range(100):
            result = service.allow_request("any-client")
            assert result.allowed is True

    def test_set_limit_overrides_default(self):
        clock = FakeClock()
        default = RateLimitConfig(max_requests=10, window_seconds=10.0)
        service = RateLimiterService(
            algorithm_class=TokenBucketLimiter,
            default_config=default,
            clock=clock,
        )

        # Set a stricter limit for client-1
        service.set_limit("client-1", RateLimitConfig(max_requests=2, window_seconds=10.0))

        service.allow_request("client-1")
        service.allow_request("client-1")
        result = service.allow_request("client-1")
        assert result.allowed is False

        # Other clients still use default (10 requests)
        for _ in range(10):
            result = service.allow_request("other-client")
            assert result.allowed is True

    def test_remove_limit_falls_back_to_default(self):
        clock = FakeClock()
        default = RateLimitConfig(max_requests=5, window_seconds=10.0)
        service = RateLimiterService(
            algorithm_class=TokenBucketLimiter,
            default_config=default,
            clock=clock,
        )

        # Set and then remove custom limit
        service.set_limit("client-1", RateLimitConfig(max_requests=1, window_seconds=10.0))
        service.remove_limit("client-1")

        # Should now use default (5 requests)
        for _ in range(5):
            result = service.allow_request("client-1")
            assert result.allowed is True

    def test_get_client_status_with_custom_limit(self):
        clock = FakeClock()
        service = RateLimiterService(
            algorithm_class=TokenBucketLimiter,
            default_config=None,
            clock=clock,
        )

        config = RateLimitConfig(max_requests=10, window_seconds=60.0)
        service.set_limit("client-1", config)
        service.allow_request("client-1")

        status = service.get_client_status("client-1")
        assert status["has_custom_limit"] is True
        assert status["config"] == config

    def test_get_client_status_without_custom_limit(self):
        clock = FakeClock()
        default = RateLimitConfig(max_requests=5, window_seconds=10.0)
        service = RateLimiterService(
            algorithm_class=TokenBucketLimiter,
            default_config=default,
            clock=clock,
        )

        status = service.get_client_status("unknown")
        assert status["has_custom_limit"] is False

    def test_set_default_limit(self):
        clock = FakeClock()
        service = RateLimiterService(
            algorithm_class=TokenBucketLimiter,
            default_config=None,
            clock=clock,
        )

        # Initially no default — everything allowed
        result = service.allow_request("client-1")
        assert result.allowed is True

        # Set a default
        service.set_default_limit(RateLimitConfig(max_requests=2, window_seconds=10.0))

        # Now unknown clients are limited
        service.allow_request("new-client")
        service.allow_request("new-client")
        result = service.allow_request("new-client")
        assert result.allowed is False

    def test_different_algorithms(self):
        clock = FakeClock()
        config = RateLimitConfig(max_requests=3, window_seconds=10.0)

        for algo_class in [TokenBucketLimiter, FixedWindowLimiter, SlidingWindowLogLimiter]:
            service = RateLimiterService(
                algorithm_class=algo_class,
                default_config=config,
                clock=clock,
            )

            for _ in range(3):
                result = service.allow_request("client")
                assert result.allowed is True

            result = service.allow_request("client")
            assert result.allowed is False

    def test_multiple_clients_independent(self):
        clock = FakeClock()
        default = RateLimitConfig(max_requests=2, window_seconds=10.0)
        service = RateLimiterService(
            algorithm_class=TokenBucketLimiter,
            default_config=default,
            clock=clock,
        )

        # Exhaust client-1
        service.allow_request("client-1")
        service.allow_request("client-1")
        result = service.allow_request("client-1")
        assert result.allowed is False

        # client-2 should be independent
        result = service.allow_request("client-2")
        assert result.allowed is True

    def test_set_limit_resets_state(self):
        clock = FakeClock()
        service = RateLimiterService(
            algorithm_class=TokenBucketLimiter,
            default_config=RateLimitConfig(max_requests=10, window_seconds=10.0),
            clock=clock,
        )

        # Give client-1 a limit and exhaust it
        service.set_limit("client-1", RateLimitConfig(max_requests=1, window_seconds=10.0))
        service.allow_request("client-1")
        result = service.allow_request("client-1")
        assert result.allowed is False

        # Re-set the limit — state should be fresh
        service.set_limit("client-1", RateLimitConfig(max_requests=1, window_seconds=10.0))
        result = service.allow_request("client-1")
        assert result.allowed is True
