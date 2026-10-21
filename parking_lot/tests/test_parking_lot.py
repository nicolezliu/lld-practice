import unittest
from datetime import datetime, timedelta

from parking_lot import (
    BestFitStrategy, Car, FirstAvailableStrategy, HourlyPricingStrategy,
    InvalidTicketError, Level, Motorcycle, ParkingFullError, ParkingLot,
    ParkingLotError, ParkingSpot, PricingStrategy, SpotAssignmentStrategy,
    SpotSize, Truck, VehicleAlreadyParkedError, VehicleType,
)


class FakeClock:
    """Controllable clock so pricing tests don't depend on real time."""

    def __init__(self, start=datetime(2026, 1, 1, 9, 0)):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, **kwargs):
        self.now += timedelta(**kwargs)


def make_lot(counts_per_level, **kwargs):
    levels = [Level.build(i, counts) for i, counts in enumerate(counts_per_level)]
    return ParkingLot(levels, **kwargs)


# ---------------------------------------------------------------- Part 1: models
class TestVehicleAndSpot(unittest.TestCase):
    def test_vehicle_types(self):
        self.assertEqual(Motorcycle("M1").vehicle_type, VehicleType.MOTORCYCLE)
        self.assertEqual(Car("C1").vehicle_type, VehicleType.CAR)
        self.assertEqual(Truck("T1").vehicle_type, VehicleType.TRUCK)

    def test_empty_plate_rejected(self):
        with self.assertRaises(ValueError):
            Car("")

    def test_fit_rules(self):
        self.assertTrue(Motorcycle("M").can_fit_in(SpotSize.SMALL))
        self.assertTrue(Motorcycle("M").can_fit_in(SpotSize.LARGE))
        self.assertFalse(Car("C").can_fit_in(SpotSize.SMALL))
        self.assertTrue(Car("C").can_fit_in(SpotSize.MEDIUM))
        self.assertFalse(Truck("T").can_fit_in(SpotSize.MEDIUM))
        self.assertTrue(Truck("T").can_fit_in(SpotSize.LARGE))

    def test_spot_park_and_unpark(self):
        spot = ParkingSpot("A1", SpotSize.MEDIUM, 0)
        car = Car("C1")
        self.assertTrue(spot.is_free)
        spot.park(car)
        self.assertFalse(spot.is_free)
        self.assertIs(spot.vehicle, car)
        self.assertIs(spot.unpark(), car)
        self.assertTrue(spot.is_free)

    def test_spot_rejects_bad_park(self):
        spot = ParkingSpot("A1", SpotSize.SMALL, 0)
        with self.assertRaises(ValueError):
            spot.park(Car("C1"))           # too big
        spot.park(Motorcycle("M1"))
        with self.assertRaises(ValueError):
            spot.park(Motorcycle("M2"))    # occupied

    def test_unpark_empty_spot_raises(self):
        with self.assertRaises(ValueError):
            ParkingSpot("A1", SpotSize.SMALL, 0).unpark()

    def test_level_build_and_available(self):
        level = Level.build(0, {SpotSize.SMALL: 2, SpotSize.LARGE: 1})
        self.assertEqual(len(level.spots), 3)
        self.assertEqual(len(level.available_spots(SpotSize.SMALL)), 2)
        self.assertEqual(len(level.available_spots(SpotSize.MEDIUM)), 0)
        self.assertEqual(len(level.available_spots()), 3)


# ---------------------------------------------------------- Part 2: park / unpark
class TestParkUnpark(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.lot = make_lot(
            [{SpotSize.SMALL: 1, SpotSize.MEDIUM: 1, SpotSize.LARGE: 1}], clock=self.clock
        )

    def test_park_returns_ticket(self):
        car = Car("C1")
        ticket = self.lot.park(car)
        self.assertIs(ticket.vehicle, car)
        self.assertEqual(ticket.entry_time, self.clock.now)
        self.assertIs(ticket.spot.vehicle, car)
        self.assertEqual(self.lot.available_spot_count(), 2)

    def test_ticket_ids_unique(self):
        t1 = self.lot.park(Car("C1"))
        t2 = self.lot.park(Motorcycle("M1"))
        self.assertNotEqual(t1.ticket_id, t2.ticket_id)

    def test_unpark_frees_spot(self):
        ticket = self.lot.park(Car("C1"))
        self.lot.unpark(ticket.ticket_id)
        self.assertTrue(ticket.spot.is_free)
        self.assertEqual(self.lot.available_spot_count(), 3)

    def test_same_vehicle_twice_rejected(self):
        self.lot.park(Car("C1"))
        with self.assertRaises(VehicleAlreadyParkedError):
            self.lot.park(Car("C1"))

    def test_vehicle_can_repark_after_leaving(self):
        t = self.lot.park(Car("C1"))
        self.lot.unpark(t.ticket_id)
        self.lot.park(Car("C1"))  # should not raise

    def test_invalid_ticket(self):
        with self.assertRaises(InvalidTicketError):
            self.lot.unpark("nope")

    def test_ticket_cannot_be_reused(self):
        t = self.lot.park(Car("C1"))
        self.lot.unpark(t.ticket_id)
        with self.assertRaises(InvalidTicketError):
            self.lot.unpark(t.ticket_id)

    def test_full_for_trucks(self):
        self.lot.park(Truck("T1"))
        with self.assertRaises(ParkingFullError):
            self.lot.park(Truck("T2"))
        self.assertFalse(self.lot.is_full())

    def test_is_full(self):
        self.lot.park(Motorcycle("M1"))
        self.lot.park(Car("C1"))
        self.lot.park(Truck("T1"))
        self.assertTrue(self.lot.is_full())
        with self.assertRaises(ParkingFullError):
            self.lot.park(Motorcycle("M2"))

    def test_errors_share_base_class(self):
        self.assertTrue(issubclass(ParkingFullError, ParkingLotError))
        self.assertTrue(issubclass(InvalidTicketError, ParkingLotError))
        self.assertTrue(issubclass(VehicleAlreadyParkedError, ParkingLotError))

    def test_find_vehicle(self):
        t = self.lot.park(Car("C1"))
        self.assertIs(self.lot.find_vehicle("C1"), t.spot)
        self.assertIsNone(self.lot.find_vehicle("ZZZ"))
        self.lot.unpark(t.ticket_id)
        self.assertIsNone(self.lot.find_vehicle("C1"))

    def test_available_count_by_size(self):
        self.lot.park(Car("C1"))  # first-available -> MEDIUM
        self.assertEqual(self.lot.available_spot_count(SpotSize.MEDIUM), 0)
        self.assertEqual(self.lot.available_spot_count(SpotSize.LARGE), 1)


# ------------------------------------------------------- Part 3: assignment strategy
class TestAssignmentStrategies(unittest.TestCase):
    def test_default_is_first_available_lowest_level(self):
        lot = make_lot([{SpotSize.LARGE: 1}, {SpotSize.MEDIUM: 1}])
        t = lot.park(Car("C1"))
        self.assertEqual(t.spot.level_number, 0)
        self.assertEqual(t.spot.size, SpotSize.LARGE)

    def test_first_available_motorcycle_takes_first_spot(self):
        lot = make_lot([{SpotSize.MEDIUM: 1, SpotSize.LARGE: 1}],
                       assignment_strategy=FirstAvailableStrategy())
        self.assertEqual(lot.park(Motorcycle("M1")).spot.size, SpotSize.MEDIUM)

    def test_best_fit_prefers_smallest_across_levels(self):
        lot = make_lot([{SpotSize.LARGE: 1}, {SpotSize.SMALL: 1}],
                       assignment_strategy=BestFitStrategy())
        t = lot.park(Motorcycle("M1"))
        self.assertEqual(t.spot.size, SpotSize.SMALL)
        self.assertEqual(t.spot.level_number, 1)

    def test_best_fit_tie_breaks_on_lowest_level(self):
        lot = make_lot([{SpotSize.MEDIUM: 1}, {SpotSize.MEDIUM: 1}],
                       assignment_strategy=BestFitStrategy())
        self.assertEqual(lot.park(Car("C1")).spot.level_number, 0)

    def test_custom_strategy_is_used(self):
        class TopLevelFirst(SpotAssignmentStrategy):
            def find_spot(self, levels, vehicle):
                for level in reversed(levels):
                    for spot in level.spots:
                        if spot.can_fit(vehicle):
                            return spot
                return None

        lot = make_lot([{SpotSize.MEDIUM: 1}, {SpotSize.MEDIUM: 1}],
                       assignment_strategy=TopLevelFirst())
        self.assertEqual(lot.park(Car("C1")).spot.level_number, 1)


# ---------------------------------------------------------- Part 4: pricing strategy
class TestPricing(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.lot = make_lot([{SpotSize.SMALL: 2, SpotSize.MEDIUM: 2, SpotSize.LARGE: 2}],
                            clock=self.clock)

    def _stay(self, vehicle, **duration):
        t = self.lot.park(vehicle)
        self.clock.advance(**duration)
        return self.lot.unpark(t.ticket_id)

    def test_default_rates(self):
        self.assertEqual(self._stay(Motorcycle("M"), hours=2), 2.0)
        self.assertEqual(self._stay(Car("C"), hours=2), 4.0)
        self.assertEqual(self._stay(Truck("T"), hours=2), 8.0)

    def test_partial_hour_rounds_up(self):
        self.assertEqual(self._stay(Car("C"), hours=1, minutes=1), 4.0)

    def test_minimum_one_hour(self):
        self.assertEqual(self._stay(Car("C"), minutes=5), 2.0)
        self.assertEqual(self._stay(Car("C2"), seconds=0), 2.0)

    def test_custom_rates(self):
        lot = make_lot([{SpotSize.MEDIUM: 1}], clock=self.clock,
                       pricing_strategy=HourlyPricingStrategy({VehicleType.CAR: 5.0}))
        t = lot.park(Car("C"))
        self.clock.advance(hours=3)
        self.assertEqual(lot.unpark(t.ticket_id), 15.0)

    def test_custom_pricing_strategy(self):
        class FlatRate(PricingStrategy):
            def calculate_fee(self, ticket, exit_time):
                return 10.0

        lot = make_lot([{SpotSize.MEDIUM: 1}], clock=self.clock, pricing_strategy=FlatRate())
        t = lot.park(Car("C"))
        self.clock.advance(hours=9)
        self.assertEqual(lot.unpark(t.ticket_id), 10.0)


if __name__ == "__main__":
    unittest.main()
