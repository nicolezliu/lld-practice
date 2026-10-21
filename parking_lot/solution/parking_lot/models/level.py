from typing import Dict, List, Optional

from ..enums import SpotSize
from .parking_spot import ParkingSpot


class Level:
    def __init__(self, level_number: int, spots: List[ParkingSpot]):
        self.level_number = level_number
        self.spots = list(spots)

    @classmethod
    def build(cls, level_number: int, counts: Dict[SpotSize, int]) -> "Level":
        """Convenience factory: Level.build(0, {SpotSize.SMALL: 2, SpotSize.LARGE: 1}).

        Spot ids look like 'L0-S1', 'L0-M1', 'L0-L1'.
        """
        spots = []
        for size in sorted(counts, key=lambda s: s.value):
            for i in range(1, counts[size] + 1):
                spot_id = f"L{level_number}-{size.name[0]}{i}"
                spots.append(ParkingSpot(spot_id, size, level_number))
        return cls(level_number, spots)

    def available_spots(self, size: Optional[SpotSize] = None) -> List[ParkingSpot]:
        return [s for s in self.spots if s.is_free and (size is None or s.size == size)]
