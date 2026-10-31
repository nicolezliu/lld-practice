"""
Phased tests for the Parking Lot system.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models only
    python -m pytest tests.py -v -k "phase2"    # Pricing only
    python -m pytest tests.py -v -k "phase3"    # ParkingLot integration

Each phase builds on the previous — start with phase1 and get all tests
green before moving on.
"""

import pytest
from datetime import datetime, timedelta

from models import (
    VehicleType, SpotSize,
    Motorcycle, Car, Truck,
    ParkingSpot, ParkingTicket,
)
from pricing import HourlyPricing, TieredPricing
from parking_lot import ParkingLot


# ===================================================================
# PHASE 1: Models — Enums, Vehicles, Spots, Tickets
# ===================================================================

class TestPhase1Enums:
    """Verify enums have the right members."""

    def test_vehicle_types_exist(self):
        assert VehicleType.MOTORCYCLE
        assert VehicleType.CAR
        assert VehicleType.TRUCK

    def test_spot_sizes_exist(self):
        assert SpotSize.SMALL
        assert SpotSize.MEDIUM
        assert SpotSize.LARGE


class TestPhase1Vehicles:
    """Verify vehicle hierarchy and fitting logic."""

    def test_motorcycle_type(self):
        m = Motorcycle("MOTO-1")
        assert m.vehicle_type == VehicleType.MOTORCYCLE

    def test_car_type(self):
        c = Car("CAR-1")
        assert c.vehicle_type == VehicleType.CAR

    def test_truck_type(self):
        t = Truck("TRUCK-1")
        assert t.vehicle_type == VehicleType.TRUCK

    def test_motorcycle_fits_all_sizes(self):
        m = Motorcycle("MOTO-1")
        assert m.can_fit_in(SpotSize.SMALL) is True
        assert m.can_fit_in(SpotSize.MEDIUM) is True
        assert m.can_fit_in(SpotSize.LARGE) is True

    def test_car_fits_medium_and_large(self):
        c = Car("CAR-1")
        assert c.can_fit_in(SpotSize.SMALL) is False
        assert c.can_fit_in(SpotSize.MEDIUM) is True
        assert c.can_fit_in(SpotSize.LARGE) is True

    def test_truck_fits_large_only(self):
        t = Truck("TRUCK-1")
        assert t.can_fit_in(SpotSize.SMALL) is False
        assert t.can_fit_in(SpotSize.MEDIUM) is False
        assert t.can_fit_in(SpotSize.LARGE) is True

    def test_vehicle_stores_license_plate(self):
        c = Car("ABC-123")
        assert c.license_plate == "ABC-123"


class TestPhase1ParkingSpot:
    """Verify spot behavior: park, remove, availability."""

    def test_new_spot_is_available(self):
        spot = ParkingSpot("S1", SpotSize.MEDIUM, floor=1)
        assert spot.is_available() is True

    def test_park_makes_spot_unavailable(self):
        spot = ParkingSpot("S1", SpotSize.MEDIUM, floor=1)
        car = Car("CAR-1")
        spot.park(car)
        assert spot.is_available() is False

    def test_remove_makes_spot_available(self):
        spot = ParkingSpot("S1", SpotSize.MEDIUM, floor=1)
        car = Car("CAR-1")
        spot.park(car)
        removed = spot.remove_vehicle()
        assert spot.is_available() is True
        assert removed is car

    def test_park_wrong_size_raises(self):
        spot = ParkingSpot("S1", SpotSize.SMALL, floor=1)
        car = Car("CAR-1")
        with pytest.raises(ValueError):
            spot.park(car)

    def test_park_occupied_raises(self):
        spot = ParkingSpot("S1", SpotSize.LARGE, floor=1)
        spot.park(Car("CAR-1"))
        with pytest.raises(ValueError):
            spot.park(Car("CAR-2"))

    def test_remove_empty_raises(self):
        spot = ParkingSpot("S1", SpotSize.MEDIUM, floor=1)
        with pytest.raises(ValueError):
            spot.remove_vehicle()


class TestPhase1Ticket:
    """Verify ticket creation."""

    def test_ticket_records_entry_time(self):
        spot = ParkingSpot("S1", SpotSize.MEDIUM, floor=1)
        car = Car("CAR-1")
        spot.park(car)
        before = datetime.now()
        ticket = ParkingTicket(car, spot)
        after = datetime.now()
        assert before <= ticket.entry_time <= after

    def test_ticket_references_vehicle_and_spot(self):
        spot = ParkingSpot("S1", SpotSize.MEDIUM, floor=1)
        car = Car("CAR-1")
        spot.park(car)
        ticket = ParkingTicket(car, spot)
        assert ticket.vehicle is car
        assert ticket.spot is spot


# ===================================================================
# PHASE 2: Pricing Strategies
# ===================================================================

class TestPhase2HourlyPricing:
    """Verify hourly pricing calculation."""

    def test_exact_hours(self):
        p = HourlyPricing(rate_per_hour=2.0)
        entry = datetime(2024, 1, 1, 10, 0)
        exit_ = datetime(2024, 1, 1, 13, 0)  # 3 hours
        assert p.calculate_fee(entry, exit_) == 6.0

    def test_partial_hour_rounds_up(self):
        p = HourlyPricing(rate_per_hour=2.0)
        entry = datetime(2024, 1, 1, 10, 0)
        exit_ = datetime(2024, 1, 1, 10, 30)  # 0.5 hours → rounds to 1
        assert p.calculate_fee(entry, exit_) == 2.0

    def test_just_over_an_hour(self):
        p = HourlyPricing(rate_per_hour=5.0)
        entry = datetime(2024, 1, 1, 10, 0)
        exit_ = datetime(2024, 1, 1, 11, 1)  # 1h1m → rounds to 2 hours
        assert p.calculate_fee(entry, exit_) == 10.0

    def test_zero_duration(self):
        p = HourlyPricing(rate_per_hour=2.0)
        entry = datetime(2024, 1, 1, 10, 0)
        assert p.calculate_fee(entry, entry) == 0.0


class TestPhase2TieredPricing:
    """Verify tiered pricing calculation."""

    def test_within_base_hours(self):
        p = TieredPricing(base_hours=2, base_rate=3.0, overflow_rate=5.0)
        entry = datetime(2024, 1, 1, 10, 0)
        exit_ = datetime(2024, 1, 1, 11, 0)  # 1 hour, within base
        assert p.calculate_fee(entry, exit_) == 3.0

    def test_exactly_at_base_hours(self):
        p = TieredPricing(base_hours=2, base_rate=3.0, overflow_rate=5.0)
        entry = datetime(2024, 1, 1, 10, 0)
        exit_ = datetime(2024, 1, 1, 12, 0)  # 2 hours
        assert p.calculate_fee(entry, exit_) == 6.0

    def test_beyond_base_hours(self):
        p = TieredPricing(base_hours=2, base_rate=3.0, overflow_rate=5.0)
        entry = datetime(2024, 1, 1, 10, 0)
        exit_ = datetime(2024, 1, 1, 14, 0)  # 4 hours → 2*3 + 2*5 = 16
        assert p.calculate_fee(entry, exit_) == 16.0

    def test_partial_overflow_hour_rounds_up(self):
        p = TieredPricing(base_hours=1, base_rate=3.0, overflow_rate=5.0)
        entry = datetime(2024, 1, 1, 10, 0)
        exit_ = datetime(2024, 1, 1, 12, 30)  # 2.5h → 1*3 + ceil(1.5)*5 = 3+10 = 13
        assert p.calculate_fee(entry, exit_) == 13.0


# ===================================================================
# PHASE 3: ParkingLot Integration
# ===================================================================

class TestPhase3ParkingLot:
    """Full integration tests for the ParkingLot."""

    def _make_lot(self) -> ParkingLot:
        return ParkingLot(
            name="Test Lot",
            num_floors=2,
            spots_per_floor={SpotSize.SMALL: 2, SpotSize.MEDIUM: 3, SpotSize.LARGE: 1},
            pricing_strategy=HourlyPricing(rate_per_hour=2.0),
        )

    def test_park_car_returns_ticket(self):
        lot = self._make_lot()
        car = Car("CAR-1")
        ticket = lot.park_vehicle(car)
        assert ticket is not None
        assert ticket.vehicle is car

    def test_park_reduces_available_spots(self):
        lot = self._make_lot()
        before = lot.get_available_spots()
        lot.park_vehicle(Car("CAR-1"))
        after = lot.get_available_spots()
        total_before = sum(before.values())
        total_after = sum(after.values())
        assert total_after == total_before - 1

    def test_unpark_restores_spot(self):
        lot = self._make_lot()
        car = Car("CAR-1")
        before = lot.get_available_spots()
        lot.park_vehicle(car)
        lot.unpark_vehicle(car)
        after = lot.get_available_spots()
        assert before == after

    def test_unpark_returns_fee(self):
        lot = self._make_lot()
        car = Car("CAR-1")
        lot.park_vehicle(car)
        fee = lot.unpark_vehicle(car)
        assert isinstance(fee, float)
        assert fee >= 0.0

    def test_unpark_unknown_vehicle_raises(self):
        lot = self._make_lot()
        with pytest.raises(ValueError):
            lot.unpark_vehicle(Car("GHOST"))

    def test_motorcycle_prefers_small_spot(self):
        lot = self._make_lot()
        moto = Motorcycle("MOTO-1")
        ticket = lot.park_vehicle(moto)
        assert ticket is not None
        # Should have taken a SMALL spot (smallest that fits)
        assert ticket.spot.size == SpotSize.SMALL

    def test_truck_only_uses_large(self):
        lot = self._make_lot()
        truck = Truck("TRUCK-1")
        ticket = lot.park_vehicle(truck)
        assert ticket is not None
        assert ticket.spot.size == SpotSize.LARGE

    def test_lot_full_returns_none(self):
        lot = self._make_lot()
        # 2 floors * 1 LARGE spot each = 2 LARGE spots total
        lot.park_vehicle(Truck("T1"))
        lot.park_vehicle(Truck("T2"))
        result = lot.park_vehicle(Truck("T3"))
        assert result is None

    def test_per_floor_availability(self):
        lot = self._make_lot()
        floor0 = lot.get_available_spots(floor=0)
        assert SpotSize.SMALL in floor0
        assert floor0[SpotSize.SMALL] == 2
        assert floor0[SpotSize.MEDIUM] == 3
        assert floor0[SpotSize.LARGE] == 1

    def test_multiple_vehicles_tracked_independently(self):
        lot = self._make_lot()
        car1 = Car("C1")
        car2 = Car("C2")
        lot.park_vehicle(car1)
        lot.park_vehicle(car2)
        lot.unpark_vehicle(car1)
        # car2 should still be parked
        with pytest.raises(ValueError):
            lot.unpark_vehicle(Car("C1"))  # already unparked (different instance, same plate — depends on impl)
