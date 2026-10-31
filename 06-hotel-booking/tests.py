"""
Phased tests for the Hotel Booking system.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models only
    python -m pytest tests.py -v -k "phase2"    # Pricing only
    python -m pytest tests.py -v -k "phase3"    # Hotel integration

Each phase builds on the previous — start with phase1 and get all tests
green before moving on.
"""

import pytest
from datetime import date, timedelta

from models import (
    RoomType, RoomStatus, BookingStatus,
    Room, Guest, Booking,
)
from pricing import StandardPricing, WeekendPremiumPricing
from hotel import Hotel


# ===================================================================
# PHASE 1: Models — Enums, Room, Guest, Booking
# ===================================================================

class TestPhase1Enums:
    """Verify enums have the right members."""

    def test_room_types_exist(self):
        assert RoomType.SINGLE
        assert RoomType.DOUBLE
        assert RoomType.SUITE

    def test_room_statuses_exist(self):
        assert RoomStatus.AVAILABLE
        assert RoomStatus.OCCUPIED
        assert RoomStatus.MAINTENANCE

    def test_booking_statuses_exist(self):
        assert BookingStatus.CONFIRMED
        assert BookingStatus.CHECKED_IN
        assert BookingStatus.CHECKED_OUT
        assert BookingStatus.CANCELLED


class TestPhase1Guest:
    """Verify Guest creation."""

    def test_guest_stores_name(self):
        g = Guest("Alice", "alice@example.com", "555-1234")
        assert g.name == "Alice"

    def test_guest_stores_email(self):
        g = Guest("Bob", "bob@example.com")
        assert g.email == "bob@example.com"

    def test_guest_stores_phone(self):
        g = Guest("Carol", "carol@example.com", "555-9999")
        assert g.phone == "555-9999"

    def test_guest_default_phone(self):
        g = Guest("Dave", "dave@example.com")
        assert g.phone == ""


class TestPhase1Room:
    """Verify Room creation and state."""

    def test_room_stores_number(self):
        r = Room("101", RoomType.SINGLE, 100.0)
        assert r.room_number == "101"

    def test_room_stores_type(self):
        r = Room("202", RoomType.DOUBLE, 150.0)
        assert r.room_type == RoomType.DOUBLE

    def test_room_stores_price(self):
        r = Room("301", RoomType.SUITE, 300.0)
        assert r.price_per_night == 300.0

    def test_room_initial_status_is_available(self):
        r = Room("101", RoomType.SINGLE, 100.0)
        assert r.status == RoomStatus.AVAILABLE


class TestPhase1Booking:
    """Verify Booking creation and validation."""

    def test_booking_stores_guest(self):
        g = Guest("Alice", "alice@example.com")
        r = Room("101", RoomType.SINGLE, 100.0)
        b = Booking(g, r, date(2025, 6, 1), date(2025, 6, 4), 300.0)
        assert b.guest is g

    def test_booking_stores_room(self):
        g = Guest("Alice", "alice@example.com")
        r = Room("101", RoomType.SINGLE, 100.0)
        b = Booking(g, r, date(2025, 6, 1), date(2025, 6, 4), 300.0)
        assert b.room is r

    def test_booking_stores_dates(self):
        g = Guest("Alice", "alice@example.com")
        r = Room("101", RoomType.SINGLE, 100.0)
        b = Booking(g, r, date(2025, 6, 1), date(2025, 6, 4), 300.0)
        assert b.check_in_date == date(2025, 6, 1)
        assert b.check_out_date == date(2025, 6, 4)

    def test_booking_stores_total_price(self):
        g = Guest("Alice", "alice@example.com")
        r = Room("101", RoomType.SINGLE, 100.0)
        b = Booking(g, r, date(2025, 6, 1), date(2025, 6, 4), 300.0)
        assert b.total_price == 300.0

    def test_booking_initial_status_is_confirmed(self):
        g = Guest("Alice", "alice@example.com")
        r = Room("101", RoomType.SINGLE, 100.0)
        b = Booking(g, r, date(2025, 6, 1), date(2025, 6, 4), 300.0)
        assert b.status == BookingStatus.CONFIRMED

    def test_booking_has_unique_id(self):
        g = Guest("Alice", "alice@example.com")
        r = Room("101", RoomType.SINGLE, 100.0)
        b1 = Booking(g, r, date(2025, 6, 1), date(2025, 6, 4), 300.0)
        b2 = Booking(g, r, date(2025, 7, 1), date(2025, 7, 4), 300.0)
        assert b1.booking_id != b2.booking_id

    def test_booking_invalid_dates_raises(self):
        g = Guest("Alice", "alice@example.com")
        r = Room("101", RoomType.SINGLE, 100.0)
        with pytest.raises(ValueError):
            Booking(g, r, date(2025, 6, 5), date(2025, 6, 3), 200.0)

    def test_booking_same_day_checkout_raises(self):
        g = Guest("Alice", "alice@example.com")
        r = Room("101", RoomType.SINGLE, 100.0)
        with pytest.raises(ValueError):
            Booking(g, r, date(2025, 6, 1), date(2025, 6, 1), 0.0)


# ===================================================================
# PHASE 2: Pricing Strategies
# ===================================================================

class TestPhase2StandardPricing:
    """Verify standard flat-rate pricing."""

    def test_one_night(self):
        p = StandardPricing()
        price = p.calculate_price(100.0, date(2025, 6, 1), date(2025, 6, 2))
        assert price == 100.0

    def test_three_nights(self):
        p = StandardPricing()
        price = p.calculate_price(100.0, date(2025, 6, 1), date(2025, 6, 4))
        assert price == 300.0

    def test_week_stay(self):
        p = StandardPricing()
        price = p.calculate_price(200.0, date(2025, 6, 1), date(2025, 6, 8))
        assert price == 1400.0

    def test_expensive_suite(self):
        p = StandardPricing()
        price = p.calculate_price(500.0, date(2025, 6, 1), date(2025, 6, 3))
        assert price == 1000.0


class TestPhase2WeekendPremiumPricing:
    """Verify weekend premium pricing."""

    def test_weekday_only_stay(self):
        """Mon Jun 2 to Thu Jun 5, 2025 — 3 weekday nights."""
        p = WeekendPremiumPricing(premium_multiplier=1.5)
        price = p.calculate_price(100.0, date(2025, 6, 2), date(2025, 6, 5))
        assert price == 300.0  # 3 * 100

    def test_weekend_only_stay(self):
        """Fri Jun 6 to Sun Jun 8, 2025 — 2 weekend nights (Fri + Sat)."""
        p = WeekendPremiumPricing(premium_multiplier=1.5)
        price = p.calculate_price(100.0, date(2025, 6, 6), date(2025, 6, 8))
        assert price == 300.0  # 2 * 100 * 1.5

    def test_mixed_stay(self):
        """Thu Jun 5 to Mon Jun 9, 2025 — Thu(100) + Fri(150) + Sat(150) + Sun(100) = 500."""
        p = WeekendPremiumPricing(premium_multiplier=1.5)
        price = p.calculate_price(100.0, date(2025, 6, 5), date(2025, 6, 9))
        assert price == 500.0

    def test_custom_multiplier(self):
        """Fri Jun 6 to Sat Jun 7, 2025 — 1 Friday night at 2x."""
        p = WeekendPremiumPricing(premium_multiplier=2.0)
        price = p.calculate_price(100.0, date(2025, 6, 6), date(2025, 6, 7))
        assert price == 200.0  # 1 * 100 * 2.0


# ===================================================================
# PHASE 3: Hotel Integration
# ===================================================================

class TestPhase3Hotel:
    """Full integration tests for the Hotel."""

    def _make_hotel(self) -> Hotel:
        """Create a test hotel with a few rooms."""
        hotel = Hotel("Test Hotel", StandardPricing())
        hotel.add_room(Room("101", RoomType.SINGLE, 100.0))
        hotel.add_room(Room("102", RoomType.SINGLE, 100.0))
        hotel.add_room(Room("201", RoomType.DOUBLE, 150.0))
        hotel.add_room(Room("202", RoomType.DOUBLE, 150.0))
        hotel.add_room(Room("301", RoomType.SUITE, 300.0))
        return hotel

    def test_search_returns_all_rooms_when_no_bookings(self):
        hotel = self._make_hotel()
        rooms = hotel.search_available_rooms(date(2025, 6, 1), date(2025, 6, 5))
        assert len(rooms) == 5

    def test_search_filters_by_room_type(self):
        hotel = self._make_hotel()
        rooms = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SUITE
        )
        assert len(rooms) == 1
        assert rooms[0].room_type == RoomType.SUITE

    def test_book_room_returns_booking(self):
        hotel = self._make_hotel()
        guest = Guest("Alice", "alice@example.com")
        rooms = hotel.search_available_rooms(date(2025, 6, 1), date(2025, 6, 4))
        booking = hotel.book_room(guest, rooms[0], date(2025, 6, 1), date(2025, 6, 4))
        assert booking is not None
        assert booking.guest is guest
        assert booking.status == BookingStatus.CONFIRMED

    def test_book_room_calculates_price(self):
        hotel = self._make_hotel()
        guest = Guest("Alice", "alice@example.com")
        # Book a SINGLE room ($100/night) for 3 nights
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 4), room_type=RoomType.SINGLE
        )[0]
        booking = hotel.book_room(guest, room, date(2025, 6, 1), date(2025, 6, 4))
        assert booking.total_price == 300.0

    def test_book_room_reduces_availability(self):
        hotel = self._make_hotel()
        guest = Guest("Alice", "alice@example.com")
        rooms_before = hotel.search_available_rooms(date(2025, 6, 1), date(2025, 6, 5))
        hotel.book_room(guest, rooms_before[0], date(2025, 6, 1), date(2025, 6, 5))
        rooms_after = hotel.search_available_rooms(date(2025, 6, 1), date(2025, 6, 5))
        assert len(rooms_after) == len(rooms_before) - 1

    def test_no_double_booking(self):
        hotel = self._make_hotel()
        guest1 = Guest("Alice", "alice@example.com")
        guest2 = Guest("Bob", "bob@example.com")
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SUITE
        )[0]
        hotel.book_room(guest1, room, date(2025, 6, 1), date(2025, 6, 5))
        # Overlapping dates on the same room should raise
        with pytest.raises(ValueError):
            hotel.book_room(guest2, room, date(2025, 6, 3), date(2025, 6, 7))

    def test_non_overlapping_booking_allowed(self):
        hotel = self._make_hotel()
        guest1 = Guest("Alice", "alice@example.com")
        guest2 = Guest("Bob", "bob@example.com")
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SUITE
        )[0]
        hotel.book_room(guest1, room, date(2025, 6, 1), date(2025, 6, 5))
        # Non-overlapping dates should work (check-out day = next check-in day is OK)
        booking2 = hotel.book_room(guest2, room, date(2025, 6, 5), date(2025, 6, 8))
        assert booking2 is not None

    def test_cancel_booking(self):
        hotel = self._make_hotel()
        guest = Guest("Alice", "alice@example.com")
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SINGLE
        )[0]
        booking = hotel.book_room(guest, room, date(2025, 6, 1), date(2025, 6, 5))
        hotel.cancel_booking(booking)
        assert booking.status == BookingStatus.CANCELLED

    def test_cancel_frees_room_for_rebooking(self):
        hotel = self._make_hotel()
        guest1 = Guest("Alice", "alice@example.com")
        guest2 = Guest("Bob", "bob@example.com")
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SUITE
        )[0]
        booking = hotel.book_room(guest1, room, date(2025, 6, 1), date(2025, 6, 5))
        hotel.cancel_booking(booking)
        # Room should now be available for rebooking
        booking2 = hotel.book_room(guest2, room, date(2025, 6, 1), date(2025, 6, 5))
        assert booking2 is not None

    def test_check_in(self):
        hotel = self._make_hotel()
        guest = Guest("Alice", "alice@example.com")
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SINGLE
        )[0]
        booking = hotel.book_room(guest, room, date(2025, 6, 1), date(2025, 6, 5))
        hotel.check_in(booking)
        assert booking.status == BookingStatus.CHECKED_IN
        assert room.status == RoomStatus.OCCUPIED

    def test_check_out(self):
        hotel = self._make_hotel()
        guest = Guest("Alice", "alice@example.com")
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SINGLE
        )[0]
        booking = hotel.book_room(guest, room, date(2025, 6, 1), date(2025, 6, 5))
        hotel.check_in(booking)
        hotel.check_out(booking)
        assert booking.status == BookingStatus.CHECKED_OUT
        assert room.status == RoomStatus.AVAILABLE

    def test_check_in_cancelled_raises(self):
        hotel = self._make_hotel()
        guest = Guest("Alice", "alice@example.com")
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SINGLE
        )[0]
        booking = hotel.book_room(guest, room, date(2025, 6, 1), date(2025, 6, 5))
        hotel.cancel_booking(booking)
        with pytest.raises(ValueError):
            hotel.check_in(booking)

    def test_check_out_without_check_in_raises(self):
        hotel = self._make_hotel()
        guest = Guest("Alice", "alice@example.com")
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SINGLE
        )[0]
        booking = hotel.book_room(guest, room, date(2025, 6, 1), date(2025, 6, 5))
        with pytest.raises(ValueError):
            hotel.check_out(booking)

    def test_invalid_date_range_raises(self):
        hotel = self._make_hotel()
        guest = Guest("Alice", "alice@example.com")
        room = hotel.search_available_rooms(
            date(2025, 6, 1), date(2025, 6, 5), room_type=RoomType.SINGLE
        )[0]
        with pytest.raises(ValueError):
            hotel.book_room(guest, room, date(2025, 6, 5), date(2025, 6, 1))

    def test_maintenance_room_excluded_from_search(self):
        hotel = self._make_hotel()
        rooms = hotel.search_available_rooms(date(2025, 6, 1), date(2025, 6, 5))
        # Put one room in maintenance
        rooms[0].status = RoomStatus.MAINTENANCE
        available = hotel.search_available_rooms(date(2025, 6, 1), date(2025, 6, 5))
        assert rooms[0] not in available
        assert len(available) == len(rooms) - 1
