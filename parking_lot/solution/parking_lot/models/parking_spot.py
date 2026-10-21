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
        return self.vehicle is None

    def can_fit(self, vehicle: Vehicle) -> bool:
        return self.is_free and vehicle.can_fit_in(self.size)

    def park(self, vehicle: Vehicle) -> None:
        if not self.can_fit(vehicle):
            raise ValueError(f"{vehicle} cannot park in spot {self.spot_id}")
        self.vehicle = vehicle

    def unpark(self) -> Vehicle:
        if self.vehicle is None:
            raise ValueError(f"spot {self.spot_id} is already empty")
        vehicle, self.vehicle = self.vehicle, None
        return vehicle

    def __repr__(self) -> str:
        return f"ParkingSpot({self.spot_id!r}, {self.size.name}, L{self.level_number})"
