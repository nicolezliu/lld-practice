"""
SOLUTION — Parking Lot System

Don't peek until you've given it a solid attempt!

This is one valid solution. Yours may differ in structure and still be
perfectly correct — there's no single "right" LLD answer. Compare your
design choices against this one and think about trade-offs.
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Optional
import math


# ===================================================================
# Enums
# ===================================================================

class VehicleType(Enum):
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    TRUCK = "TRUCK"


class SpotSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3


# ===================================================================
# Vehicle hierarchy
# ===================================================================

class Vehicle(ABC):
    def __init__(self, license_plate: str):
        self._license_plate = license_plate

    @property
    def license_plate(self) -> str:
        return self._license_plate

    @property
    @abstractmethod
    def vehicle_type(self) -> VehicleType:
        ...

    @abstractmethod
    def can_fit_in(self, spot_size: SpotSize) -> bool:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._license_plate})"


class Motorcycle(Vehicle):
    @property
    def vehicle_type(self) -> VehicleType:
        return VehicleType.MOTORCYCLE

    def can_fit_in(self, spot_size: SpotSize) -> bool:
        return True  # fits in any spot


class Car(Vehicle):
    @property
    def vehicle_type(self) -> VehicleType:
        return VehicleType.CAR

    def can_fit_in(self, spot_size: SpotSize) -> bool:
        return spot_size in (SpotSize.MEDIUM, SpotSize.LARGE)


class Truck(Vehicle):
    @property
    def vehicle_type(self) -> VehicleType:
        return VehicleType.TRUCK

    def can_fit_in(self, spot_size: SpotSize) -> bool:
        return spot_size == SpotSize.LARGE


# ===================================================================
# Parking infrastructure
# ===================================================================

class ParkingSpot:
    def __init__(self, spot_id: str, size: SpotSize, floor: int):
        self._spot_id = spot_id
        self._size = size
        self._floor = floor
        self._vehicle: Optional[Vehicle] = None

    @property
    def spot_id(self) -> str:
        return self._spot_id

    @property
    def size(self) -> SpotSize:
        return self._size

    @property
    def floor(self) -> int:
        return self._floor

    @property
    def vehicle(self) -> Optional[Vehicle]:
        return self._vehicle

    def is_available(self) -> bool:
        return self._vehicle is None

    def park(self, vehicle: Vehicle) -> None:
        if not self.is_available():
            raise ValueError(f"Spot {self._spot_id} is already occupied")
        if not vehicle.can_fit_in(self._size):
            raise ValueError(
                f"{vehicle} cannot fit in {self._size.name} spot"
            )
        self._vehicle = vehicle

    def remove_vehicle(self) -> Vehicle:
        if self.is_available():
            raise ValueError(f"Spot {self._spot_id} is already empty")
        vehicle = self._vehicle
        self._vehicle = None
        return vehicle

    def __repr__(self) -> str:
        status = self._vehicle.license_plate if self._vehicle else "FREE"
        return f"Spot({self._spot_id}, {self._size.name}, {status})"


class ParkingTicket:
    def __init__(self, vehicle: Vehicle, spot: ParkingSpot):
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()

    def __repr__(self) -> str:
        return (
            f"Ticket(vehicle={self.vehicle.license_plate}, "
            f"spot={self.spot.spot_id}, entry={self.entry_time})"
        )


# ===================================================================
# Pricing strategies (Strategy pattern)
# ===================================================================

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, entry_time: datetime, exit_time: datetime) -> float:
        ...


class HourlyPricing(PricingStrategy):
    def __init__(self, rate_per_hour: float):
        self._rate = rate_per_hour

    def calculate_fee(self, entry_time: datetime, exit_time: datetime) -> float:
        duration = (exit_time - entry_time).total_seconds()
        if duration <= 0:
            return 0.0
        hours = math.ceil(duration / 3600)
        return hours * self._rate


class TieredPricing(PricingStrategy):
    def __init__(self, base_hours: int, base_rate: float, overflow_rate: float):
        self._base_hours = base_hours
        self._base_rate = base_rate
        self._overflow_rate = overflow_rate

    def calculate_fee(self, entry_time: datetime, exit_time: datetime) -> float:
        duration = (exit_time - entry_time).total_seconds()
        if duration <= 0:
            return 0.0
        total_hours = duration / 3600
        if total_hours <= self._base_hours:
            return math.ceil(total_hours) * self._base_rate
        base_fee = self._base_hours * self._base_rate
        overflow_hours = total_hours - self._base_hours
        overflow_fee = math.ceil(overflow_hours) * self._overflow_rate
        return base_fee + overflow_fee


# ===================================================================
# ParkingLot (the orchestrator)
# ===================================================================

class ParkingLot:
    """
    Key design decisions in this solution:

    1. Spots are sorted by size (SMALL first) so _find_spot naturally
       returns the smallest fit — this avoids wasting LARGE spots on
       motorcycles.

    2. Active tickets are keyed by the Vehicle object. An alternative
       would be to key by license plate string — trade-off is whether
       you want identity-based or value-based lookup.

    3. Thread safety is NOT implemented here. In production you'd wrap
       park_vehicle / unpark_vehicle with a threading.Lock.
    """

    def __init__(
        self,
        name: str,
        num_floors: int,
        spots_per_floor: dict[SpotSize, int],
        pricing_strategy: PricingStrategy,
    ):
        self._name = name
        self._pricing = pricing_strategy
        self._spots: list[ParkingSpot] = []
        self._active_tickets: dict[Vehicle, ParkingTicket] = {}

        # Create spots — sorted by size so smallest are tried first
        for floor in range(num_floors):
            for size in [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE]:
                count = spots_per_floor.get(size, 0)
                for i in range(count):
                    spot_id = f"F{floor}-{size.name[0]}{i}"
                    self._spots.append(ParkingSpot(spot_id, size, floor))

    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingTicket]:
        spot = self._find_spot(vehicle)
        if spot is None:
            return None
        spot.park(vehicle)
        ticket = ParkingTicket(vehicle, spot)
        self._active_tickets[vehicle] = ticket
        return ticket

    def unpark_vehicle(self, vehicle: Vehicle) -> float:
        ticket = self._active_tickets.get(vehicle)
        if ticket is None:
            raise ValueError(f"Vehicle {vehicle.license_plate} is not in the lot")
        ticket.spot.remove_vehicle()
        exit_time = datetime.now()
        fee = self._pricing.calculate_fee(ticket.entry_time, exit_time)
        del self._active_tickets[vehicle]
        return fee

    def get_available_spots(self, floor: Optional[int] = None) -> dict[SpotSize, int]:
        counts = {size: 0 for size in SpotSize}
        for spot in self._spots:
            if floor is not None and spot.floor != floor:
                continue
            if spot.is_available():
                counts[spot.size] += 1
        return counts

    def _find_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Find smallest available spot that fits the vehicle."""
        for spot in self._spots:
            if spot.is_available() and vehicle.can_fit_in(spot.size):
                return spot
        return None
