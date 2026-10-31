# Rate Limiter — LLD Practice

## Problem Statement
Design a rate limiter that controls the frequency of requests from clients.
The system should support multiple rate-limiting algorithms, per-client
configuration, and return clear allow/deny decisions with quota information.

## Requirements

### Functional
- Support multiple rate-limiting algorithms:
  - **Token Bucket** — tokens refill at a steady rate, each request consumes one token
  - **Fixed Window** — requests counted in fixed time windows, counter resets at boundary
  - **Sliding Window Log** — tracks exact timestamps, counts requests in a rolling window
- Per-client rate limiting with independent configurations
- Configurable limits (max requests per time window)
- Return allow/deny decisions with remaining quota info (remaining count, retry-after)
- Default limits for unknown/unconfigured clients
- Ability to reset a client's rate-limit state

### Non-Functional
- O(1) time complexity for allow/deny decisions (Token Bucket, Fixed Window)
- Thread-safety considerations (noted in design, not required in skeleton)
- Clean separation between algorithm logic and client management

## Suggested Design Patterns
- **Strategy** — for selecting the rate-limiting algorithm
- **Factory** — for creating limiter instances with different configurations
- **Template Method** — common structure across algorithm implementations

## Your Task
1. Define the result and config data classes in `models.py`
2. Implement the rate-limiting algorithms in `algorithms.py`
3. Wire up the per-client service in `rate_limiter.py`
4. Run `main.py` to see rate limiting in action
5. Try swapping algorithms and observe different behavior

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models — RateLimitResult, RateLimitConfig
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: Algorithms — TokenBucket, FixedWindow, SlidingWindowLog
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: RateLimiterService integration
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Add distributed rate limiting (shared state across multiple instances)
- Add weighted requests (some requests cost more tokens than others)
- Add a sliding window counter algorithm (hybrid of fixed window and sliding log)
- Add rate-limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
