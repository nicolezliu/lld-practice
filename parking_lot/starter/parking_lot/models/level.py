from typing import Dict, List, Optional

from ..enums import SpotSize
from .parking_spot import ParkingSpot


class Level:
    def __init__(self, level_number: int, spots: List[ParkingSpot]):
        self.level_number = level_number
        self.spots = list(spots)

    @classmethod
    def build(cls, level_number: int, counts: Dict[SpotSize, int]) -> "Level":
        """Factory: Level.build(0, {SpotSize.SMALL: 2, SpotSize.LARGE: 1}).

        Create spots in size order SMALL -> MEDIUM -> LARGE.
        Suggested ids: 'L0-S1', 'L0-S2', 'L0-L1'.
        """
        # TODO
        raise NotImplementedError

    def available_spots(self, size: Optional[SpotSize] = None) -> List[ParkingSpot]:
        """Free spots on this level, optionally filtered by size."""
        # TODO
        raise NotImplementedError
