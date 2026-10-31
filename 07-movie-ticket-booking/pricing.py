"""
Pricing strategies for the Movie Ticket Booking system.

Your job: implement the Strategy pattern here.
- Define an abstract PricingStrategy
- Implement at least two concrete strategies
- Think about: how would you add a "holiday surcharge" without modifying existing code?
"""

from abc import ABC, abstractmethod
from datetime import datetime

# NOTE: import SeatType from models — but be aware of circular imports.
# In your skeleton files, models.py has no dependency on pricing.py,
# and pricing.py imports from models.py. Keep it that way.
from models import Seat, SeatType


class PricingStrategy(ABC):
    """Abstract pricing strategy — calculates the price for a list of seats."""

    @abstractmethod
    def calculate_price(self, seats: list[Seat], show_time: datetime) -> float:
        """
        Calculate the total price for the given seats at the given show time.

        Args:
            seats: list of seats being booked
            show_time: the start time of the show (might affect pricing)

        Returns:
            Total price in dollars.
        """
        ...


class StandardPricing(PricingStrategy):
    """
    Base price multiplied by a seat-type factor.

    Factors:
    - REGULAR: 1.0x
    - PREMIUM: 1.5x
    - VIP:     2.5x

    Example: base_price=10.0, 2 REGULAR + 1 VIP = 2*10 + 1*25 = $45.00
    """

    def __init__(self, base_price: float):
        # TODO: store base_price, define seat type multipliers
        pass

    def calculate_price(self, seats: list[Seat], show_time: datetime) -> float:
        # TODO: sum up base_price * multiplier for each seat's type
        pass


class PeakHourPricing(PricingStrategy):
    """
    Same as standard pricing, but adds a surcharge for shows
    starting between 6 PM and 9 PM (18:00–21:00 inclusive start hour).

    Think about:
    - This could wrap/decorate a StandardPricing (Decorator pattern)
    - Or it could be standalone with its own multipliers + surcharge
    - Either approach is valid — pick one and implement it
    """

    def __init__(self, base_price: float, peak_surcharge: float):
        """
        Args:
            base_price: base ticket price
            peak_surcharge: flat surcharge added PER SEAT during peak hours
        """
        # TODO: store base_price, peak_surcharge
        pass

    def calculate_price(self, seats: list[Seat], show_time: datetime) -> float:
        # TODO:
        # 1. Calculate standard price (base * seat-type multiplier)
        # 2. If show_time.hour is between 18 and 21 (inclusive), add surcharge per seat
        pass


# STRETCH: Add a PromotionalPricing that applies a percentage discount,
#          or a WeekendPricing with day-of-week surcharges.
