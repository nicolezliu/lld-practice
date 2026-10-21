from datetime import datetime
from typing import Callable, List, Optional

from .enums import SpotSize
from .exceptions import InvalidTicketError, ParkingFullError, VehicleAlreadyParkedError
from .models.level import Level
from .models.parking_spot import ParkingSpot
from .models.ticket import Ticket
from .models.vehicle import Vehicle
from .strategies.pricing import HourlyPricingStrategy, PricingStrategy
from .strategies.spot_assignment import FirstAvailableStrategy, SpotAssignmentStrategy


class ParkingLot:
    """Main entry point. Coordinates levels, strategies, and active tickets.

    Defaults when an argument is None:
      assignment_strategy -> FirstAvailableStrategy()
      pricing_strategy    -> HourlyPricingStrategy()
      clock               -> datetime.now   (tests pass a fake clock)
    """

    def __init__(
        self,
        levels: List[Level],
        assignment_strategy: Optional[SpotAssignmentStrategy] = None,
        pricing_strategy: Optional[PricingStrategy] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        # TODO
        raise NotImplementedError

    def park(self, vehicle: Vehicle) -> Ticket:
        """Assign a spot and return a Ticket with a unique ticket_id.
        Raise VehicleAlreadyParkedError if this plate is already in the lot.
        Raise ParkingFullError if no spot fits."""
        # TODO
        raise NotImplementedError

    def unpark(self, ticket_id: str) -> float:
        """Free the spot and return the fee.
        Raise InvalidTicketError for unknown or already-used tickets."""
        # TODO
        raise NotImplementedError

    def find_vehicle(self, license_plate: str) -> Optional[ParkingSpot]:
        """Spot the vehicle is parked in, or None."""
        # TODO
        raise NotImplementedError

    def available_spot_count(self, size: Optional[SpotSize] = None) -> int:
        # TODO
        raise NotImplementedError

    def is_full(self) -> bool:
        # TODO
        raise NotImplementedError
