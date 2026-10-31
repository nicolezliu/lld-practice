"""
Pricing strategies for the Parking Lot.

Your job: implement the Strategy pattern here.
- Define an abstract PricingStrategy
- Implement at least two concrete strategies
- Think about: how would you add a "weekend surcharge" without modifying existing code?
"""

from abc import ABC, abstractmethod
from datetime import datetime


class PricingStrategy(ABC):
    """Abstract pricing strategy — calculates fee based on entry and exit times."""

    @abstractmethod
    def calculate_fee(self, entry_time: datetime, exit_time: datetime) -> float:
        """Calculate the parking fee. Return the amount in dollars."""
        ...


class HourlyPricing(PricingStrategy):
    """
    Charges a flat rate per hour (rounded up).

    Example: rate_per_hour=2.0 → 3.5 hours costs $8.00
    """

    def __init__(self, rate_per_hour: float):
        # TODO
        pass

    def calculate_fee(self, entry_time: datetime, exit_time: datetime) -> float:
        # TODO: calculate hours (round up), multiply by rate
        pass


class TieredPricing(PricingStrategy):
    """
    First N hours at one rate, remaining hours at a different rate.

    Example: first 2 hours at $3/hr, then $5/hr after that.
    """

    def __init__(self, base_hours: int, base_rate: float, overflow_rate: float):
        # TODO
        pass

    def calculate_fee(self, entry_time: datetime, exit_time: datetime) -> float:
        # TODO
        pass


# STRETCH: Add a FlatRatePricing, WeekendSurchargePricing (decorator pattern?), etc.
