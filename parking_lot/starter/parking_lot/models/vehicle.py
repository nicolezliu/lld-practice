from abc import ABC

from ..enums import SpotSize, VehicleType


class Vehicle(ABC):
    """Base vehicle.

    Fit rules:
      - Motorcycle fits SMALL, MEDIUM, LARGE
      - Car fits MEDIUM, LARGE
      - Truck fits LARGE only
    """

    def __init__(self, license_plate: str):
        # TODO: store license_plate; raise ValueError if it's empty
        raise NotImplementedError

    def can_fit_in(self, size: SpotSize) -> bool:
        # TODO
        raise NotImplementedError


class Motorcycle(Vehicle):
    # TODO: set vehicle_type (and whatever you need for fit rules)
    pass


class Car(Vehicle):
    # TODO
    pass


class Truck(Vehicle):
    # TODO
    pass
