from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.level import Level
from ..models.parking_spot import ParkingSpot
from ..models.vehicle import Vehicle


class SpotAssignmentStrategy(ABC):
    """Strategy pattern: decides WHICH free spot a vehicle gets."""

    @abstractmethod
    def find_spot(self, levels: List[Level], vehicle: Vehicle) -> Optional[ParkingSpot]:
        ...


class FirstAvailableStrategy(SpotAssignmentStrategy):
    """Lowest level first, then spot order within the level. Any fitting size."""

    def find_spot(self, levels, vehicle):
        for level in levels:
            for spot in level.spots:
                if spot.can_fit(vehicle):
                    return spot
        return None


class BestFitStrategy(SpotAssignmentStrategy):
    """Smallest fitting spot size anywhere in the lot (saves big spots for big vehicles).
    Ties are broken by lowest level, then spot order."""

    def find_spot(self, levels, vehicle):
        best = None
        for level in levels:
            for spot in level.spots:
                if spot.can_fit(vehicle) and (best is None or spot.size.value < best.size.value):
                    best = spot
        return best
