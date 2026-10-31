"""
Models for the Elevator System.

Your job: fill in the class bodies.
- Think about elevator state transitions (IDLE → MOVING_UP → DOOR_OPEN → ...)
- Think about how requests are represented
- Think about what events/changes an observer would care about
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Direction(Enum):
    """Direction of travel."""
    UP = "UP"
    DOWN = "DOWN"


class ElevatorState(Enum):
    """
    Possible states of an elevator.
    
    Think about valid transitions:
    - IDLE → MOVING_UP, MOVING_DOWN
    - MOVING_UP → DOOR_OPEN, IDLE
    - DOOR_OPEN → MOVING_UP, MOVING_DOWN, IDLE
    """
    # TODO: define members
    pass


class DoorState(Enum):
    """Door state — separate from elevator movement state."""
    # TODO: define members
    pass


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

@dataclass
class FloorRequest:
    """
    A request to go to a specific floor.
    
    This could be:
    - An EXTERNAL request (someone on floor 3 presses UP)
    - An INTERNAL request (someone inside elevator presses floor 7)
    
    Think about: do you need to distinguish these? Why might that matter
    for the dispatcher?
    """
    floor: int
    direction: Direction | None = None  # None for internal requests
    # TODO: add any additional fields you think are needed


# ---------------------------------------------------------------------------
# Elevator
# ---------------------------------------------------------------------------

class Elevator:
    """
    A single elevator car.
    
    Think about:
    - What state does it track? (current floor, direction, door state, requests)
    - How does it decide where to go next?
    - How does it handle the door open/close cycle?
    - What's the capacity model?
    """

    def __init__(self, elevator_id: int, capacity: int, total_floors: int):
        """
        Args:
            elevator_id: unique identifier
            capacity: maximum number of passengers
            total_floors: number of floors in the building (for bounds checking)
        """
        # TODO: initialize state
        # - current_floor (start at ground floor / floor 0)
        # - state (IDLE initially)
        # - door_state
        # - set of pending floor requests
        # - current passenger count
        pass

    def add_request(self, floor: int) -> None:
        """
        Add a destination floor to this elevator's queue.
        
        Raise ValueError if the floor is out of range.
        """
        # TODO
        pass

    def move_one_floor(self) -> None:
        """
        Move the elevator one floor in its current direction.
        
        Think about:
        - What if it reaches the top/bottom floor?
        - What if it has no more requests in the current direction?
        """
        # TODO
        pass

    def should_stop(self) -> bool:
        """Return True if the elevator should stop at the current floor."""
        # TODO: check if current floor is in the request set
        pass

    def open_doors(self) -> None:
        """Open doors and remove the current floor from requests."""
        # TODO
        pass

    def close_doors(self) -> None:
        """Close the doors."""
        # TODO
        pass

    @property
    def is_idle(self) -> bool:
        """True if the elevator has no pending requests."""
        # TODO
        pass

    def __repr__(self) -> str:
        # TODO: useful debug representation
        return f"Elevator({self.elevator_id})"
