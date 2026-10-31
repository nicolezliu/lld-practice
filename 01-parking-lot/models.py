"""
Models for the Parking Lot system.

Your job: fill in the class bodies.
- Think about what data each class needs to hold
- Think about relationships (does ParkingFloor OWN spots? or just reference them?)
- Think about what should be an enum vs a class vs an abstract base class
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class VehicleType(Enum):
    """Types of vehicles the lot supports."""
    # TODO: define members
    pass


class SpotSize(Enum):
    """Sizes of parking spots."""
    # TODO: define members
    pass


# ---------------------------------------------------------------------------
# Vehicle hierarchy
# ---------------------------------------------------------------------------

class Vehicle(ABC):
    """
    Base class for all vehicles.

    Think about:
    - What identifies a vehicle? (license plate?)
    - What determines which spots it can fit in?
    """

    def __init__(self, license_plate: str):
        # TODO: store license plate, set vehicle_type
        pass

    @property
    @abstractmethod
    def vehicle_type(self) -> VehicleType:
        """Return the type of this vehicle."""
        ...

    @abstractmethod
    def can_fit_in(self, spot_size: SpotSize) -> bool:
        """Return True if this vehicle can park in a spot of the given size."""
        ...


class Motorcycle(Vehicle):
    """A motorcycle — fits in any spot size."""

    # TODO: implement vehicle_type property and can_fit_in
    pass


class Car(Vehicle):
    """A car — fits in MEDIUM or LARGE spots."""

    # TODO: implement vehicle_type property and can_fit_in
    pass


class Truck(Vehicle):
    """A truck — only fits in LARGE spots."""

    # TODO: implement vehicle_type property and can_fit_in
    pass


# ---------------------------------------------------------------------------
# Parking infrastructure
# ---------------------------------------------------------------------------

class ParkingSpot:
    """
    A single parking spot.

    Think about:
    - What state does a spot have? (occupied/free, which vehicle is in it)
    - How do you assign/release a vehicle?
    - Should assigning a vehicle that doesn't fit raise an error?
    """

    def __init__(self, spot_id: str, size: SpotSize, floor: int):
        # TODO: initialize spot state
        pass

    def is_available(self) -> bool:
        """Return True if the spot is free."""
        # TODO
        pass

    def park(self, vehicle: Vehicle) -> None:
        """
        Park a vehicle in this spot.
        Raise ValueError if the spot is occupied or the vehicle doesn't fit.
        """
        # TODO
        pass

    def remove_vehicle(self) -> Vehicle:
        """
        Remove and return the parked vehicle.
        Raise ValueError if the spot is already empty.
        """
        # TODO
        pass


class ParkingTicket:
    """
    Issued when a vehicle enters the lot.

    Think about:
    - What info does a ticket carry?
    - Entry time, spot reference, vehicle reference?
    """

    def __init__(self, vehicle: Vehicle, spot: ParkingSpot):
        # TODO: store references, record entry_time
        pass
