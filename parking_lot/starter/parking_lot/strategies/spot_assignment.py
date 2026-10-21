from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.level import Level
from ..models.parking_spot import ParkingSpot
from ..models.vehicle import Vehicle


class SpotAssignmentStrategy(ABC):
    """Strategy pattern: decides WHICH free spot a vehicle gets. (Provided.)"""

    @abstractmethod
    def find_spot(self, levels: List[Level], vehicle: Vehicle) -> Optional[ParkingSpot]:
        ...


class FirstAvailableStrategy(SpotAssignmentStrategy):
    """Lowest level first, then spot order within the level. Any size that fits.
    Return None if nothing fits."""

    def find_spot(self, levels, vehicle):
        # TODO
        raise NotImplementedError


class BestFitStrategy(SpotAssignmentStrategy):
    """Smallest fitting spot SIZE anywhere in the lot.
    Ties: lowest level, then spot order. Return None if nothing fits."""

    def find_spot(self, levels, vehicle):
        # TODO
        raise NotImplementedError
