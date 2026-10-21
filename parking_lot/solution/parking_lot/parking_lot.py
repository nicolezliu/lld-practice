import itertools
from datetime import datetime
from typing import Callable, Dict, List, Optional

from .enums import SpotSize
from .exceptions import InvalidTicketError, ParkingFullError, VehicleAlreadyParkedError
from .models.level import Level
from .models.parking_spot import ParkingSpot
from .models.ticket import Ticket
from .models.vehicle import Vehicle
from .strategies.pricing import HourlyPricingStrategy, PricingStrategy
from .strategies.spot_assignment import FirstAvailableStrategy, SpotAssignmentStrategy


class ParkingLot:
    """Facade that coordinates levels, strategies, and active tickets.

    Dependencies are injected so behavior can change without editing this class
    (Open/Closed + Dependency Inversion).
    """

    def __init__(
        self,
        levels: List[Level],
        assignment_strategy: Optional[SpotAssignmentStrategy] = None,
        pricing_strategy: Optional[PricingStrategy] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ):
        self.levels = sorted(levels, key=lambda lvl: lvl.level_number)
        self.assignment_strategy = assignment_strategy or FirstAvailableStrategy()
        self.pricing_strategy = pricing_strategy or HourlyPricingStrategy()
        self.clock = clock or datetime.now
        self._active_tickets: Dict[str, Ticket] = {}
        self._plate_to_ticket: Dict[str, str] = {}
        self._ticket_counter = itertools.count(1)

    def park(self, vehicle: Vehicle) -> Ticket:
        if vehicle.license_plate in self._plate_to_ticket:
            raise VehicleAlreadyParkedError(vehicle.license_plate)
        spot = self.assignment_strategy.find_spot(self.levels, vehicle)
        if spot is None:
            raise ParkingFullError(f"no spot for {vehicle}")
        spot.park(vehicle)
        ticket = Ticket(f"T{next(self._ticket_counter)}", vehicle, spot, self.clock())
        self._active_tickets[ticket.ticket_id] = ticket
        self._plate_to_ticket[vehicle.license_plate] = ticket.ticket_id
        return ticket

    def unpark(self, ticket_id: str) -> float:
        ticket = self._active_tickets.pop(ticket_id, None)
        if ticket is None:
            raise InvalidTicketError(ticket_id)
        fee = self.pricing_strategy.calculate_fee(ticket, self.clock())
        ticket.spot.unpark()
        del self._plate_to_ticket[ticket.vehicle.license_plate]
        return fee

    def find_vehicle(self, license_plate: str) -> Optional[ParkingSpot]:
        ticket_id = self._plate_to_ticket.get(license_plate)
        return self._active_tickets[ticket_id].spot if ticket_id else None

    def available_spot_count(self, size: Optional[SpotSize] = None) -> int:
        return sum(len(level.available_spots(size)) for level in self.levels)

    def is_full(self) -> bool:
        return self.available_spot_count() == 0
