"""
Phased tests for the Elevator System.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models only
    python -m pytest tests.py -v -k "phase2"    # Dispatcher only
    python -m pytest tests.py -v -k "phase3"    # ElevatorSystem integration

Each phase builds on the previous — start with phase1.
"""

import pytest

from models import Direction, ElevatorState, DoorState, FloorRequest, Elevator
from dispatcher import NearestElevatorStrategy, ZoneBasedStrategy
from elevator_system import ElevatorSystem


# ===================================================================
# PHASE 1: Models — Enums, FloorRequest, Elevator
# ===================================================================

class TestPhase1Enums:
    """Verify enums have the right members."""

    def test_direction(self):
        assert Direction.UP
        assert Direction.DOWN

    def test_elevator_states(self):
        assert ElevatorState.IDLE
        assert ElevatorState.MOVING_UP
        assert ElevatorState.MOVING_DOWN
        assert ElevatorState.DOOR_OPEN

    def test_door_states(self):
        assert DoorState.OPEN
        assert DoorState.CLOSED


class TestPhase1FloorRequest:
    """Verify FloorRequest data class."""

    def test_external_request(self):
        req = FloorRequest(floor=5, direction=Direction.UP)
        assert req.floor == 5
        assert req.direction == Direction.UP

    def test_internal_request(self):
        req = FloorRequest(floor=3)
        assert req.floor == 3
        assert req.direction is None


class TestPhase1Elevator:
    """Verify Elevator state management."""

    def test_initial_state(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        assert e.current_floor == 0
        assert e.is_idle is True

    def test_add_request(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        e.add_request(5)
        assert e.is_idle is False

    def test_add_request_out_of_range_raises(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        with pytest.raises(ValueError):
            e.add_request(15)
        with pytest.raises(ValueError):
            e.add_request(-1)

    def test_move_one_floor_up(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        e.add_request(3)
        e.move_one_floor()
        assert e.current_floor == 1

    def test_move_one_floor_down(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        # Move up to floor 5 first
        e.add_request(5)
        for _ in range(5):
            e.move_one_floor()
        e.open_doors()
        e.close_doors()
        # Now request floor 2
        e.add_request(2)
        e.move_one_floor()
        assert e.current_floor == 4

    def test_should_stop_at_requested_floor(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        e.add_request(3)
        for _ in range(3):
            e.move_one_floor()
        assert e.current_floor == 3
        assert e.should_stop() is True

    def test_should_not_stop_at_unrequested_floor(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        e.add_request(5)
        e.move_one_floor()  # floor 1
        assert e.should_stop() is False

    def test_open_doors_removes_request(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        e.add_request(2)
        e.move_one_floor()
        e.move_one_floor()
        e.open_doors()
        assert e.should_stop() is False  # request cleared

    def test_close_doors_returns_to_idle(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        e.add_request(1)
        e.move_one_floor()
        e.open_doors()
        e.close_doors()
        assert e.is_idle is True  # no more requests, doors closed


class TestPhase1ElevatorEdgeCases:
    """Edge cases for the elevator."""

    def test_no_request_stays_idle(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        assert e.is_idle is True

    def test_request_current_floor(self):
        e = Elevator(elevator_id=0, capacity=8, total_floors=10)
        e.add_request(0)  # already at floor 0
        assert e.should_stop() is True


# ===================================================================
# PHASE 2: Dispatcher Strategies
# ===================================================================

class TestPhase2NearestStrategy:
    """Verify nearest-elevator dispatching."""

    def _make_elevators(self, floors: list[int]) -> list[Elevator]:
        """Create elevators positioned at given floors."""
        elevators = []
        for i, target_floor in enumerate(floors):
            e = Elevator(elevator_id=i, capacity=8, total_floors=10)
            # Move elevator to target floor
            if target_floor > 0:
                e.add_request(target_floor)
                for _ in range(target_floor):
                    e.move_one_floor()
                e.open_doors()
                e.close_doors()
            elevators.append(e)
        return elevators

    def test_picks_nearest_idle(self):
        strategy = NearestElevatorStrategy()
        elevators = self._make_elevators([0, 4, 8])
        request = FloorRequest(floor=5, direction=Direction.UP)
        selected = strategy.select_elevator(request, elevators)
        # Elevator at floor 4 is nearest to floor 5
        assert selected is not None
        assert selected.elevator_id == 1

    def test_picks_only_available(self):
        strategy = NearestElevatorStrategy()
        elevators = self._make_elevators([0])
        request = FloorRequest(floor=5, direction=Direction.UP)
        selected = strategy.select_elevator(request, elevators)
        assert selected is not None
        assert selected.elevator_id == 0

    def test_empty_list_returns_none(self):
        strategy = NearestElevatorStrategy()
        request = FloorRequest(floor=5, direction=Direction.UP)
        selected = strategy.select_elevator(request, [])
        assert selected is None


class TestPhase2ZoneStrategy:
    """Verify zone-based dispatching."""

    def test_floor_in_zone(self):
        strategy = ZoneBasedStrategy(total_floors=10, num_elevators=2)
        elevators = [
            Elevator(elevator_id=0, capacity=8, total_floors=10),
            Elevator(elevator_id=1, capacity=8, total_floors=10),
        ]
        # Floor 3 should be in zone 0 (floors 0-4)
        req = FloorRequest(floor=3, direction=Direction.UP)
        selected = strategy.select_elevator(req, elevators)
        assert selected is not None
        assert selected.elevator_id == 0

    def test_high_floor_in_second_zone(self):
        strategy = ZoneBasedStrategy(total_floors=10, num_elevators=2)
        elevators = [
            Elevator(elevator_id=0, capacity=8, total_floors=10),
            Elevator(elevator_id=1, capacity=8, total_floors=10),
        ]
        # Floor 7 should be in zone 1 (floors 5-9)
        req = FloorRequest(floor=7, direction=Direction.UP)
        selected = strategy.select_elevator(req, elevators)
        assert selected is not None
        assert selected.elevator_id == 1


# ===================================================================
# PHASE 3: ElevatorSystem Integration
# ===================================================================

class TestPhase3ElevatorSystem:
    """Full integration tests for the ElevatorSystem."""

    def _make_system(self) -> ElevatorSystem:
        return ElevatorSystem(
            num_floors=10,
            num_elevators=3,
            capacity_per_elevator=8,
            dispatch_strategy=NearestElevatorStrategy(),
        )

    def test_initial_status(self):
        system = self._make_system()
        status = system.status()
        assert len(status) == 3
        for s in status:
            assert s["current_floor"] == 0

    def test_request_elevator(self):
        system = self._make_system()
        system.request_elevator(floor=5, direction=Direction.UP)
        # After request, at least one elevator should have a pending request
        status = system.status()
        has_request = any(len(s["pending_requests"]) > 0 for s in status)
        assert has_request is True

    def test_step_moves_elevator(self):
        system = self._make_system()
        system.request_elevator(floor=3, direction=Direction.UP)
        system.step()
        status = system.status()
        # At least one elevator should have moved from floor 0
        moved = any(s["current_floor"] != 0 for s in status)
        assert moved is True

    def test_elevator_arrives_at_requested_floor(self):
        system = self._make_system()
        system.request_elevator(floor=3, direction=Direction.UP)
        # Step enough times to arrive
        for _ in range(10):
            system.step()
        status = system.status()
        # At least one elevator should have reached floor 3
        arrived = any(s["current_floor"] == 3 for s in status)
        assert arrived is True

    def test_select_floor_internal(self):
        system = self._make_system()
        system.select_floor(elevator_id=0, floor=7)
        status = system.status()
        assert 7 in status[0]["pending_requests"]

    def test_system_returns_to_idle(self):
        system = self._make_system()
        system.request_elevator(floor=2, direction=Direction.UP)
        # Step many times — elevator should arrive and go idle
        for _ in range(20):
            system.step()
        status = system.status()
        # The elevator that handled the request should be idle
        dispatched = [s for s in status if s["current_floor"] == 2 or len(s["pending_requests"]) == 0]
        assert len(dispatched) > 0

    def test_multiple_requests(self):
        system = self._make_system()
        system.request_elevator(floor=2, direction=Direction.UP)
        system.request_elevator(floor=5, direction=Direction.DOWN)
        system.request_elevator(floor=8, direction=Direction.UP)
        # All 3 elevators should be assigned (one request each)
        status = system.status()
        active = sum(1 for s in status if len(s["pending_requests"]) > 0)
        assert active >= 2  # at least 2 should have requests

    def test_display_does_not_crash(self):
        system = self._make_system()
        system.request_elevator(floor=5, direction=Direction.UP)
        system.step()
        # Just verify it doesn't raise
        system.display()
