from enum import Enum


class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"


class SpotSize(Enum):
    # Values give an ordering: SMALL < MEDIUM < LARGE
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
