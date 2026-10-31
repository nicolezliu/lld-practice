"""
Test driver for the Rate Limiter system.

Run this to verify your implementation:
    python main.py

Start with the basic scenarios, then add your own edge cases.
"""

import time

from models import RateLimitConfig
from algorithms import TokenBucketLimiter, FixedWindowLimiter, SlidingWindowLogLimiter
from rate_limiter import RateLimiterService


def main():
    print("=" * 60)
    print("RATE LIMITER — LLD PRACTICE")
    print("=" * 60)

    # --- Scenario 1: Basic token bucket limiting ---
    print("\n--- Scenario 1: Token Bucket — 5 requests per 10 seconds ---")
    config = RateLimitConfig(max_requests=5, window_seconds=10.0)
    limiter = TokenBucketLimiter(config)

    for i in range(7):
        result = limiter.allow("client-1")
        status = "ALLOWED" if result.allowed else "DENIED"
        print(
            f"  Request {i + 1}: {status} "
            f"(remaining={result.remaining}, retry_after={result.retry_after})"
        )

    # --- Scenario 2: Fixed window with reset ---
    print("\n--- Scenario 2: Fixed Window — 3 requests per 2 seconds ---")
    config = RateLimitConfig(max_requests=3, window_seconds=2.0)
    limiter = FixedWindowLimiter(config)

    print("  Sending 4 requests immediately...")
    for i in range(4):
        result = limiter.allow("client-1")
        status = "ALLOWED" if result.allowed else "DENIED"
        print(f"    Request {i + 1}: {status} (remaining={result.remaining})")

    print("  Waiting 2 seconds for window to reset...")
    time.sleep(2.0)

    result = limiter.allow("client-1")
    status = "ALLOWED" if result.allowed else "DENIED"
    print(f"    After wait: {status} (remaining={result.remaining})")

    # --- Scenario 3: Sliding window precision ---
    print("\n--- Scenario 3: Sliding Window Log — 3 requests per 2 seconds ---")
    config = RateLimitConfig(max_requests=3, window_seconds=2.0)
    limiter = SlidingWindowLogLimiter(config)

    print("  Sending 3 requests over 1 second...")
    for i in range(3):
        result = limiter.allow("client-1")
        status = "ALLOWED" if result.allowed else "DENIED"
        print(f"    Request {i + 1}: {status}")
        if i < 2:
            time.sleep(0.5)

    result = limiter.allow("client-1")
    print(f"    Request 4: {'ALLOWED' if result.allowed else 'DENIED'} "
          f"(retry_after={result.retry_after:.2f}s)" if result.retry_after else "")

    # --- Scenario 4: RateLimiterService with per-client limits ---
    print("\n--- Scenario 4: Service — per-client limits ---")
    default = RateLimitConfig(max_requests=5, window_seconds=10.0)
    service = RateLimiterService(
        algorithm_class=TokenBucketLimiter,
        default_config=default,
    )

    # VIP client gets more requests
    service.set_limit("vip-client", RateLimitConfig(max_requests=20, window_seconds=10.0))

    print("  Regular client (5 req limit):")
    for i in range(6):
        result = service.allow_request("regular-client")
        status = "ALLOWED" if result.allowed else "DENIED"
        print(f"    Request {i + 1}: {status}")

    print("  VIP client (20 req limit):")
    for i in range(6):
        result = service.allow_request("vip-client")
        status = "ALLOWED" if result.allowed else "DENIED"
        print(f"    Request {i + 1}: {status}")

    # --- Scenario 5: Multiple algorithms comparison ---
    print("\n--- Scenario 5: Algorithm comparison (3 req / 5 sec) ---")
    config = RateLimitConfig(max_requests=3, window_seconds=5.0)

    algorithms = [
        ("Token Bucket", TokenBucketLimiter),
        ("Fixed Window", FixedWindowLimiter),
        ("Sliding Log ", SlidingWindowLogLimiter),
    ]

    for name, algo_class in algorithms:
        limiter = algo_class(config)
        results = []
        for _ in range(5):
            r = limiter.allow("test")
            results.append("O" if r.allowed else "X")
        print(f"  {name}: {' '.join(results)}")

    # --- Add your own scenarios below! ---
    # Ideas:
    #   - What happens when you remove a client's limit?
    #   - Try changing the default limit at runtime
    #   - Compare token bucket refill behavior vs fixed window reset
    #   - Stress test with many concurrent clients


if __name__ == "__main__":
    main()
