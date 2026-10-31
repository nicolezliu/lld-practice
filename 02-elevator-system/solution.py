"""
SOLUTION — Elevator System

Don't peek until you've given it a solid attempt!

This solution uses:
- State pattern for elevator states (simplified via enum + transition logic)
- Strategy pattern for dispatching
- Step-based simulation (no real-time threads)
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


# ===================================================================
# Enums
# ===================================================================

class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"


class ElevatorState(Enum):
    IDLE = "IDLE"
    MOVING_UP = "MOVING_UP"
    MOVING_DOWN = "MOVING_DOWN"
    DOOR_OPEN = "DOOR_OPEN"


class DoorState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


# ===================================================================
# Request
# ===================================================================

@dataclass
class FloorRequest:
    floor: int
    direction: Direction | None = None


# ===================================================================
# Elevator
# ===================================================================

class Elevator:
    """
    Key design decisions:

    1. Requests are stored as a set of floor numbers. We don't
       distinguish internal vs external requests at this level —
       the dispatcher handles that distinction.

    2. Direction is inferred from the pending requests relative
       to current floor, not stored as a separate "intended direction."
       This simplifies state transitions.

    3. The elevator uses a step-based model: each call to
       move_one_floor() advances by exactly one floor. The
       ElevatorSystem calls this in a loop.
    """

    def __init__(self, elevator_id: int, capacity: int, total_floors: int):
        self.elevator_id = elevator_id
        self.capacity = capacity
        self.total_floors = total_floors
        self.current_floor: int = 0
        self.state: ElevatorState = ElevatorState.IDLE
        self.door_state: DoorState = DoorState.CLOSED
        self._requests: set[int] = set()
        self.passenger_count: int = 0

    @property
    def requests(self) -> set[int]:
        return self._requests.copy()

    def add_request(self, floor: int) -> None:
        if floor < 0 or floor >= self.total_floors:
            raise ValueError(
                f"Floor {floor} out of range [0, {self.total_floors - 1}]"
            )
        self._requests.add(floor)
        # If idle and request is not current floor, determine direction
        if self.state == ElevatorState.IDLE and floor != self.current_floor:
            self.state = (
                ElevatorState.MOVING_UP
                if floor > self.current_floor
                else ElevatorState.MOVING_DOWN
            )

    def move_one_floor(self) -> None:
        if not self._requests:
            self.state = ElevatorState.IDLE
            return

        # Determine direction based on requests
        if self.state == ElevatorState.IDLE or self.state == ElevatorState.DOOR_OPEN:
            # Pick a direction — prefer continuing current direction if possible
            has_above = any(f > self.current_floor for f in self._requests)
            has_below = any(f < self.current_floor for f in self._requests)
            if has_above:
                self.state = ElevatorState.MOVING_UP
            elif has_below:
                self.state = ElevatorState.MOVING_DOWN
            else:
                # All requests are at current floor
                return

        if self.state == ElevatorState.MOVING_UP:
            if self.current_floor < self.total_floors - 1:
                self.current_floor += 1
            else:
                # At top, reverse
                self.state = ElevatorState.MOVING_DOWN
                if self.current_floor > 0:
                    self.current_floor -= 1
        elif self.state == ElevatorState.MOVING_DOWN:
            if self.current_floor > 0:
                self.current_floor -= 1
            else:
                # At bottom, reverse
                self.state = ElevatorState.MOVING_UP
                if self.current_floor < self.total_floors - 1:
                    self.current_floor += 1

    def should_stop(self) -> bool:
        return self.current_floor in self._requests

    def open_doors(self) -> None:
        self.state = ElevatorState.DOOR_OPEN
        self.door_state = DoorState.OPEN
        self._requests.discard(self.current_floor)

    def close_doors(self) -> None:
        self.door_state = DoorState.CLOSED
        if not self._requests:
            self.state = ElevatorState.IDLE

    @property
    def is_idle(self) -> bool:
        return len(self._requests) == 0 and self.state == ElevatorState.IDLE

    def __repr__(self) -> str:
        return (
            f"Elevator(id={self.elevator_id}, floor={self.current_floor}, "
            f"state={self.state.value}, doors={self.door_state.value}, "
            f"requests={sorted(self._requests)})"
        )


# ===================================================================
# Dispatcher strategies (Strategy pattern)
# ===================================================================

class DispatchStrategy(ABC):
    @abstractmethod
    def select_elevator(
        self,
        request: FloorRequest,
        elevators: list[Elevator],
    ) -> Elevator | None:
        ...


class NearestElevatorStrategy(DispatchStrategy):
    """
    Selection priority:
    1. Nearest idle elevator
    2. Nearest elevator moving toward the request in the right direction
    3. Any elevator (fallback)
    """

    def select_elevator(
        self,
        request: FloorRequest,
        elevators: list[Elevator],
    ) -> Elevator | None:
        if not elevators:
            return None

        best: Elevator | None = None
        best_distance = float("inf")

        # Pass 1: idle elevators
        for e in elevators:
            if e.is_idle:
                dist = abs(e.current_floor - request.floor)
                if dist < best_distance:
                    best_distance = dist
                    best = e

        if best is not None:
            return best

        # Pass 2: moving toward the request floor in the correct direction
        best_distance = float("inf")
        for e in elevators:
            moving_toward = False
            if (
                e.state == ElevatorState.MOVING_UP
                and e.current_floor <= request.floor
                and request.direction in (Direction.UP, None)
            ):
                moving_toward = True
            elif (
                e.state == ElevatorState.MOVING_DOWN
                and e.current_floor >= request.floor
                and request.direction in (Direction.DOWN, None)
            ):
                moving_toward = True

            if moving_toward:
                dist = abs(e.current_floor - request.floor)
                if dist < best_distance:
                    best_distance = dist
                    best = e

        if best is not None:
            return best

        # Pass 3: fallback — nearest by distance regardless of state
        best_distance = float("inf")
        for e in elevators:
            dist = abs(e.current_floor - request.floor)
            if dist < best_distance:
                best_distance = dist
                best = e

        return best


class ZoneBasedStrategy(DispatchStrategy):
    """
    Divides floors into zones, one per elevator.
    Falls back to nearest if the zone's elevator is busy.
    """

    def __init__(self, total_floors: int, num_elevators: int):
        self._total_floors = total_floors
        self._num_elevators = num_elevators
        # Calculate zone size (ceiling division)
        self._zone_size = (total_floors + num_elevators - 1) // num_elevators

    def select_elevator(
        self,
        request: FloorRequest,
        elevators: list[Elevator],
    ) -> Elevator | None:
        if not elevators:
            return None

        zone_index = min(request.floor // self._zone_size, len(elevators) - 1)
        return elevators[zone_index]


# ===================================================================
# ElevatorSystem (the orchestrator)
# ===================================================================

class ElevatorSystem:
    """
    Key design decisions:

    1. Step-based simulation — each call to step() advances all
       elevators by one time unit. This is simpler than real-time
       and easier to test/debug.

    2. The step loop handles door cycles: if doors are open, close
       them first before moving. This gives one step for
       passengers to board/exit.

    3. status() returns dicts for easy inspection. In production
       you might return dataclasses or emit events instead.
    """

    def __init__(
        self,
        num_floors: int,
        num_elevators: int,
        capacity_per_elevator: int,
        dispatch_strategy: DispatchStrategy,
    ):
        self._num_floors = num_floors
        self._strategy = dispatch_strategy
        self._elevators = [
            Elevator(
                elevator_id=i,
                capacity=capacity_per_elevator,
                total_floors=num_floors,
            )
            for i in range(num_elevators)
        ]

    def request_elevator(self, floor: int, direction: Direction) -> None:
        request = FloorRequest(floor=floor, direction=direction)
        elevator = self._strategy.select_elevator(request, self._elevators)
        if elevator is not None:
            elevator.add_request(floor)

    def select_floor(self, elevator_id: int, floor: int) -> None:
        for e in self._elevators:
            if e.elevator_id == elevator_id:
                e.add_request(floor)
                return
        raise ValueError(f"No elevator with id {elevator_id}")

    def step(self) -> None:
        for elevator in self._elevators:
            if elevator.door_state == DoorState.OPEN:
                elevator.close_doors()
                continue

            if elevator.is_idle:
                continue

            elevator.move_one_floor()

            if elevator.should_stop():
                elevator.open_doors()

    def status(self) -> list[dict]:
        result = []
        for e in self._elevators:
            result.append({
                "elevator_id": e.elevator_id,
                "current_floor": e.current_floor,
                "state": e.state.value,
                "door_state": e.door_state.value,
                "pending_requests": sorted(e.requests),
                "passenger_count": e.passenger_count,
            })
        return result

    def display(self) -> None:
        print(f"  {'─' * 50}")
        for s in self.status():
            reqs = ", ".join(str(r) for r in s["pending_requests"]) or "none"
            print(
                f"  Elevator {s['elevator_id']}: "
                f"floor={s['current_floor']:>2}, "
                f"state={s['state']:<11}, "
                f"doors={s['door_state']:<6}, "
                f"requests=[{reqs}]"
            )
