import math
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional

from ..enums import VehicleType
from ..models.ticket import Ticket


class PricingStrategy(ABC):
    """Strategy pattern: decides HOW MUCH a stay costs."""

    @abstractmethod
    def calculate_fee(self, ticket: Ticket, exit_time: datetime) -> float:
        ...


class HourlyPricingStrategy(PricingStrategy):
    """Per-vehicle-type hourly rate. Partial hours round UP. Minimum charge is 1 hour."""

    DEFAULT_RATES = {
        VehicleType.MOTORCYCLE: 1.0,
        VehicleType.CAR: 2.0,
        VehicleType.TRUCK: 4.0,
    }

    def __init__(self, rates: Optional[Dict[VehicleType, float]] = None):
        self.rates = dict(rates) if rates is not None else dict(self.DEFAULT_RATES)

    def calculate_fee(self, ticket, exit_time):
        seconds = (exit_time - ticket.entry_time).total_seconds()
        if seconds < 0:
            raise ValueError("exit_time is before entry_time")
        hours = max(1, math.ceil(seconds / 3600))
        return hours * self.rates[ticket.vehicle.vehicle_type]
