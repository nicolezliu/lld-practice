from abc import ABC

from ..enums import SpotSize, VehicleType


class Vehicle(ABC):
    """Base vehicle. Subclasses declare their type and which spot sizes fit them."""

    vehicle_type: VehicleType
    allowed_spot_sizes: frozenset

    def __init__(self, license_plate: str):
        if not license_plate:
            raise ValueError("license_plate is required")
        self.license_plate = license_plate

    def can_fit_in(self, size: SpotSize) -> bool:
        return size in self.allowed_spot_sizes

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.license_plate!r})"


class Motorcycle(Vehicle):
    vehicle_type = VehicleType.MOTORCYCLE
    allowed_spot_sizes = frozenset({SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE})


class Car(Vehicle):
    vehicle_type = VehicleType.CAR
    allowed_spot_sizes = frozenset({SpotSize.MEDIUM, SpotSize.LARGE})


class Truck(Vehicle):
    vehicle_type = VehicleType.TRUCK
    allowed_spot_sizes = frozenset({SpotSize.LARGE})
