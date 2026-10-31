"""
Core Parking Lot logic.

Your job: implement the ParkingLot class.
This is the main entry point — it orchestrates spots, tickets, and pricing.

Think about:
- How do you efficiently find an available spot for a given vehicle?
- How do you handle the case where the lot is full?
- Should this be a Singleton?
"""

from typing import Optional
from models import (
    Vehicle, ParkingSpot, ParkingTicket, SpotSize, VehicleType
)
from pricing import PricingStrategy


class ParkingLot:
    """
    The main parking lot system.

    Manages floors, spots, active tickets, and pricing.
    """

    def __init__(
        self,
        name: str,
        num_floors: int,
        spots_per_floor: dict[SpotSize, int],
        pricing_strategy: PricingStrategy,
    ):
        """
        Initialize the parking lot.

        Args:
            name: name of the parking lot
            num_floors: number of floors
            spots_per_floor: dict mapping SpotSize → count per floor
                e.g. {SpotSize.SMALL: 10, SpotSize.MEDIUM: 20, SpotSize.LARGE: 5}
            pricing_strategy: the pricing strategy to use
        """
        # TODO: create all ParkingSpot instances
        # TODO: initialize a mapping for active tickets (vehicle → ticket)
        pass

    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingTicket]:
        """
        Find an available spot for the vehicle and issue a ticket.

        Returns:
            ParkingTicket if a spot was found, None if the lot is full for this vehicle type.
        """
        # TODO:
        # 1. Find the smallest available spot that fits the vehicle
        # 2. Park the vehicle in the spot
        # 3. Create and store a ticket
        # 4. Return the ticket
        pass

    def unpark_vehicle(self, vehicle: Vehicle) -> float:
        """
        Remove a vehicle from its spot and calculate the fee.

        Returns:
            The parking fee.

        Raises:
            ValueError: if the vehicle is not in the lot.
        """
        # TODO:
        # 1. Look up the ticket for this vehicle
        # 2. Remove the vehicle from the spot
        # 3. Calculate the fee using the pricing strategy
        # 4. Clean up the ticket
        # 5. Return the fee
        pass

    def get_available_spots(self, floor: Optional[int] = None) -> dict[SpotSize, int]:
        """
        Return a count of available spots grouped by size.
        If floor is specified, only count that floor.
        """
        # TODO
        pass

    def _find_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """
        Find the best available spot for a vehicle.

        Strategy: prefer the smallest spot that fits (to save larger spots).
        """
        # TODO
        pass
