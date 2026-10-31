"""
Pricing strategies for the Hotel Booking system.

Your job: implement the Strategy pattern here.
- Define an abstract PricingStrategy
- Implement at least two concrete strategies
- Think about: how would you add a "holiday surcharge" without modifying existing code?
"""

from abc import ABC, abstractmethod
from datetime import date

# Forward reference — pricing needs to know the room's base price
# but we avoid circular imports by accepting price_per_night as a float.


class PricingStrategy(ABC):
    """Abstract pricing strategy — calculates total booking cost."""

    @abstractmethod
    def calculate_price(
        self,
        price_per_night: float,
        check_in: date,
        check_out: date,
    ) -> float:
        """
        Calculate the total price for a stay.

        Args:
            price_per_night: the room's base nightly rate
            check_in: arrival date
            check_out: departure date

        Returns:
            Total price for the stay.
        """
        ...


class StandardPricing(PricingStrategy):
    """
    Flat rate per night — simply multiplies base price by number of nights.

    Example: $100/night for 3 nights = $300
    """

    def calculate_price(
        self,
        price_per_night: float,
        check_in: date,
        check_out: date,
    ) -> float:
        # TODO: calculate number of nights, multiply by price_per_night
        pass


class WeekendPremiumPricing(PricingStrategy):
    """
    Higher rate on weekend nights (Friday and Saturday).

    A "night" is defined by its start date:
    - Friday night (date is Friday) → premium rate
    - Saturday night (date is Saturday) → premium rate
    - All other nights → base rate

    Example: premium_multiplier=1.5 means weekends cost 50% more.
    """

    def __init__(self, premium_multiplier: float = 1.5):
        # TODO: store the multiplier
        pass

    def calculate_price(
        self,
        price_per_night: float,
        check_in: date,
        check_out: date,
    ) -> float:
        # TODO:
        # 1. Iterate over each night of the stay
        # 2. Check if the night's date falls on Friday (4) or Saturday (5)
        # 3. Apply premium_multiplier for weekend nights, base rate otherwise
        # 4. Sum up the total
        pass


# STRETCH: Add a SeasonalPricing strategy (holiday surcharge)
# STRETCH: Add a PromotionalPricing strategy (discount for long stays)
