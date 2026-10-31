"""
Models for the Rate Limiter system.

Your job: fill in the class bodies.
- Think about what information a caller needs after a rate-limit check
- Think about what configuration a rate limiter needs
- Think about how these data classes will be used by the algorithms
"""

from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class RateLimitResult:
    """
    The outcome of a rate-limit check.

    Think about:
    - Does the caller need to know if the request was allowed or denied?
    - How many requests remain in the current window?
    - When can a denied client retry?
    - What is the configured limit?
    """
    allowed: bool        # TODO: was the request allowed?
    remaining: int       # TODO: how many requests remain before hitting the limit?
    retry_after: Optional[float]  # TODO: seconds until the client can retry (None if allowed)
    limit: int           # TODO: the configured max requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class RateLimitConfig:
    """
    Configuration for a rate limiter.

    Think about:
    - What defines a rate limit? (count + time window)
    - Should these be mutable or immutable?
    - What validation might you add?
    """
    max_requests: int     # TODO: maximum number of requests allowed in the window
    window_seconds: float  # TODO: the time window duration in seconds
