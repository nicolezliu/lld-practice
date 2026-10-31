"""
Elevator dispatching strategies.

Your job: implement the Strategy pattern for elevator dispatching.
- The dispatcher decides WHICH elevator should handle an external request
- This is the key algorithmic decision in the system

Think about trade-offs:
- Simple nearest-elevator is easy but can starve distant floors
- Direction-aware dispatching is smarter but more complex
- SCAN algorithm (like disk scheduling) is efficient but less intuitive
"""

from abc import ABC, abstractmethod
from models import Elevator, Direction, FloorRequest


class DispatchStrategy(ABC):
    """Abstract dispatcher — picks the best elevator for a request."""

    @abstractmethod
    def select_elevator(
        self,
        request: FloorRequest,
        elevators: list[Elevator],
    ) -> Elevator | None:
        """
        Select the best elevator to handle this request.
        
        Args:
            request: the floor request to fulfill
            elevators: all available elevators
            
        Returns:
            The selected Elevator, or None if no elevator can take the request.
        """
        ...


class NearestElevatorStrategy(DispatchStrategy):
    """
    Pick the closest idle elevator.
    If no idle elevator, pick the closest one moving toward the request floor
    in the right direction.
    
    Simple but effective for low-traffic buildings.
    """

    def select_elevator(
        self,
        request: FloorRequest,
        elevators: list[Elevator],
    ) -> Elevator | None:
        # TODO:
        # 1. Filter to idle elevators, pick the nearest
        # 2. If none idle, filter to elevators moving toward request floor
        #    in the correct direction
        # 3. If still none, pick any elevator (will handle it eventually)
        pass


class ZoneBasedStrategy(DispatchStrategy):
    """
    Assign each elevator a "zone" of floors.
    Elevator 0 handles floors 0-4, Elevator 1 handles 5-9, etc.
    
    Good for tall buildings with predictable traffic.
    
    Think about: what happens when one zone is busy and another is empty?
    """

    def __init__(self, total_floors: int, num_elevators: int):
        # TODO: calculate zone boundaries
        pass

    def select_elevator(
        self,
        request: FloorRequest,
        elevators: list[Elevator],
    ) -> Elevator | None:
        # TODO: find which zone the request floor falls in
        pass


# STRETCH: Implement a SCAN (elevator algorithm) strategy
# STRETCH: Implement a load-balanced strategy that considers passenger count
