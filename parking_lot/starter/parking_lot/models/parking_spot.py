from typing import Optional

from ..enums import SpotSize
from .vehicle import Vehicle


class ParkingSpot:
    def __init__(self, spot_id: str, size: SpotSize, level_number: int):
        self.spot_id = spot_id
        self.size = size
        self.level_number = level_number
        self.vehicle: Optional[Vehicle] = None

    @property
    def is_free(self) -> bool:
        # TODO
        raise NotImplementedError

    def can_fit(self, vehicle: Vehicle) -> bool:
        """True if the spot is free AND the vehicle fits this size."""
        # TODO
        raise NotImplementedError

    def park(self, vehicle: Vehicle) -> None:
        """Raise ValueError if the spot is taken or the vehicle doesn't fit."""
        # TODO
        raise NotImplementedError

    def unpark(self) -> Vehicle:
        """Remove and return the vehicle. Raise ValueError if empty."""
        # TODO
        raise NotImplementedError
