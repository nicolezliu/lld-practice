"""
The Elevator System — orchestrates elevators, dispatching, and simulation.

Your job: implement the ElevatorSystem class that ties everything together.

Think about:
- How does the simulation loop work? (step-by-step, not real-time)
- How do external requests differ from internal requests?
- How do you report system status?
"""

from models import Elevator, FloorRequest, Direction
from dispatcher import DispatchStrategy


class ElevatorSystem:
    """
    Manages multiple elevators in a building.
    
    This is the public API that users interact with.
    """

    def __init__(
        self,
        num_floors: int,
        num_elevators: int,
        capacity_per_elevator: int,
        dispatch_strategy: DispatchStrategy,
    ):
        """
        Args:
            num_floors: total floors in the building (0-indexed)
            num_elevators: number of elevator cars
            capacity_per_elevator: max passengers per elevator
            dispatch_strategy: the dispatching algorithm to use
        """
        # TODO: create elevators, store strategy
        pass

    def request_elevator(self, floor: int, direction: Direction) -> None:
        """
        External request: someone on a floor presses the UP or DOWN button.
        
        The dispatcher picks which elevator should handle it.
        """
        # TODO:
        # 1. Create a FloorRequest
        # 2. Use the dispatch strategy to pick an elevator
        # 3. Add the floor to that elevator's request queue
        pass

    def select_floor(self, elevator_id: int, floor: int) -> None:
        """
        Internal request: a passenger inside an elevator presses a floor button.
        """
        # TODO: find the elevator by ID, add the floor request
        pass

    def step(self) -> None:
        """
        Advance the simulation by one time step.
        
        Each elevator should:
        1. If doors are open → close them
        2. If it has requests → move one floor
        3. If it should stop at current floor → open doors
        4. If no requests → go idle
        """
        # TODO: iterate over all elevators and advance their state
        pass

    def status(self) -> list[dict]:
        """
        Return the current status of all elevators.
        
        Each entry should include: elevator_id, current_floor, state,
        door_state, pending_requests, passenger_count.
        """
        # TODO
        pass

    def display(self) -> None:
        """Print a human-readable status of the system."""
        # TODO: format and print status nicely
        pass
