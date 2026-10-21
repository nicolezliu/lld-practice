from dataclasses import dataclass
from datetime import datetime

from .parking_spot import ParkingSpot
from .vehicle import Vehicle


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    vehicle: Vehicle
    spot: ParkingSpot
    entry_time: datetime
