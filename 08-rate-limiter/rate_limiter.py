"""
Rate Limiter Service — manages per-client rate limiters.

Your job: implement the RateLimiterService class that ties everything together.

Think about:
- How do you manage different rate limits for different clients?
- What happens when an unknown client makes a request?
- How do you allow runtime reconfiguration?
- Should the service own the algorithm choice, or should callers specify it?
"""

import time
from typing import Callable, Optional

from models import RateLimitResult, RateLimitConfig
from algorithms import RateLimiter, TokenBucketLimiter


class RateLimiterService:
    """
    Manages per-client rate limiters.

    This is the public API that application code interacts with.
    It wraps the algorithm details and provides client-level management.

    Think about:
    - How do you store per-client limiters?
    - What's the default behavior for unknown clients?
    - How does set_limit interact with existing client state?
    """

    def __init__(
        self,
        algorithm_class: type[RateLimiter] = TokenBucketLimiter,
        default_config: Optional[RateLimitConfig] = None,
        clock: Callable[[], float] = time.time,
    ):
        """
        Args:
            algorithm_class: which RateLimiter subclass to use for new clients
            default_config: default rate-limit config for unknown clients
                           (if None, unknown clients are always allowed)
            clock: a callable that returns the current time in seconds
        """
        # TODO: store algorithm class, default config, clock
        # TODO: initialize per-client limiter storage
        pass

    def set_limit(self, client_id: str, config: RateLimitConfig) -> None:
        """
        Set or update the rate limit for a specific client.

        Creates a new limiter instance with the given config.
        If the client already has a limiter, it is replaced (state is reset).
        """
        # TODO: create a new limiter for this client using algorithm_class
        pass

    def remove_limit(self, client_id: str) -> None:
        """
        Remove the rate limit for a specific client.

        After removal, the client falls back to the default limit
        (or is always allowed if no default is set).
        """
        # TODO: remove the client's limiter
        pass

    def allow_request(self, client_id: str) -> RateLimitResult:
        """
        Check if a request from the given client should be allowed.

        Lookup order:
        1. Client-specific limiter (if set via set_limit)
        2. Default limiter (if default_config was provided)
        3. Always allow (if no default_config)

        Returns:
            RateLimitResult with the decision and quota info.
        """
        # TODO:
        # 1. Check for client-specific limiter
        # 2. If not found, use or create a default limiter for this client
        # 3. If no default config, allow the request unconditionally
        pass

    def get_client_status(self, client_id: str) -> dict:
        """
        Return the current rate-limit status for a client.

        Useful for monitoring and debugging.

        Returns a dict with:
        - has_custom_limit: bool
        - config: the active RateLimitConfig (or None)
        - result: the current RateLimitResult (without consuming a request)
        """
        # TODO: build and return a status dict
        pass

    def set_default_limit(self, config: RateLimitConfig) -> None:
        """
        Set or update the default rate limit for unknown clients.

        Existing default limiters for clients that haven't been given
        a custom limit should be replaced.
        """
        # TODO: update the default config and clear any default-based limiters
        pass
