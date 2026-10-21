from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional

from ..enums import VehicleType
from ..models.ticket import Ticket


class PricingStrategy(ABC):
    """Strategy pattern: decides HOW MUCH a stay costs. (Provided.)"""

    @abstractmethod
    def calculate_fee(self, ticket: Ticket, exit_time: datetime) -> float:
        ...


class HourlyPricingStrategy(PricingStrategy):
    """Per-vehicle-type hourly rate.
      - Partial hours round UP (1h01m = 2 hours)
      - Minimum charge is 1 hour (even 0 minutes)
      - Default rates: motorcycle $1, car $2, truck $4
      - `rates` overrides the defaults
    """

    DEFAULT_RATES = {
        VehicleType.MOTORCYCLE: 1.0,
        VehicleType.CAR: 2.0,
        VehicleType.TRUCK: 4.0,
    }

    def __init__(self, rates: Optional[Dict[VehicleType, float]] = None):
        # TODO
        raise NotImplementedError

    def calculate_fee(self, ticket, exit_time):
        # TODO
        raise NotImplementedError
