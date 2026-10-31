"""
Phased tests for the Movie Ticket Booking system.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models only
    python -m pytest tests.py -v -k "phase2"    # Pricing only
    python -m pytest tests.py -v -k "phase3"    # BookingSystem integration

Each phase builds on the previous — start with phase1 and get all tests
green before moving on.
"""

import pytest
from datetime import datetime, date

from models import (
    SeatType, SeatStatus, BookingStatus,
    Seat, Movie, Screen, Show, Booking,
)
from pricing import StandardPricing, PeakHourPricing
from booking_system import MovieBookingSystem


# ===================================================================
# PHASE 1: Models — Enums, Seat, Movie, Screen, Show, Booking
# ===================================================================

class TestPhase1Enums:
    """Verify enums have the right members."""

    def test_seat_types_exist(self):
        assert SeatType.REGULAR
        assert SeatType.PREMIUM
        assert SeatType.VIP

    def test_seat_statuses_exist(self):
        assert SeatStatus.AVAILABLE
        assert SeatStatus.BOOKED
        assert SeatStatus.BLOCKED

    def test_booking_statuses_exist(self):
        assert BookingStatus.CONFIRMED
        assert BookingStatus.CANCELLED


class TestPhase1Seat:
    """Verify Seat construction and identity."""

    def test_seat_attributes(self):
        seat = Seat("A", 1, SeatType.REGULAR)
        assert seat.row == "A"
        assert seat.number == 1
        assert seat.seat_type == SeatType.REGULAR

    def test_seat_id(self):
        seat = Seat("B", 5, SeatType.PREMIUM)
        assert seat.seat_id == "B5"

    def test_seat_equality(self):
        s1 = Seat("A", 1, SeatType.REGULAR)
        s2 = Seat("A", 1, SeatType.REGULAR)
        assert s1 == s2

    def test_seat_inequality(self):
        s1 = Seat("A", 1, SeatType.REGULAR)
        s2 = Seat("A", 2, SeatType.REGULAR)
        assert s1 != s2

    def test_seat_hash_consistent(self):
        s1 = Seat("A", 1, SeatType.REGULAR)
        s2 = Seat("A", 1, SeatType.REGULAR)
        assert hash(s1) == hash(s2)
        assert len({s1, s2}) == 1  # same seat in a set


class TestPhase1Movie:
    """Verify Movie construction."""

    def test_movie_attributes(self):
        movie = Movie("Inception", 148, "Sci-Fi")
        assert movie.title == "Inception"
        assert movie.duration_minutes == 148
        assert movie.genre == "Sci-Fi"


class TestPhase1Screen:
    """Verify Screen construction and seat lookup."""

    def _make_screen(self) -> Screen:
        seats = [
            Seat("A", 1, SeatType.REGULAR),
            Seat("A", 2, SeatType.REGULAR),
            Seat("B", 1, SeatType.PREMIUM),
            Seat("B", 2, SeatType.VIP),
        ]
        return Screen("Screen-1", seats)

    def test_screen_capacity(self):
        screen = self._make_screen()
        assert screen.capacity == 4

    def test_get_seat_by_id(self):
        screen = self._make_screen()
        seat = screen.get_seat("B1")
        assert seat is not None
        assert seat.seat_type == SeatType.PREMIUM

    def test_get_seat_not_found(self):
        screen = self._make_screen()
        assert screen.get_seat("Z9") is None


class TestPhase1Show:
    """Verify Show seat tracking."""

    def _make_show(self) -> Show:
        seats = [
            Seat("A", 1, SeatType.REGULAR),
            Seat("A", 2, SeatType.REGULAR),
            Seat("B", 1, SeatType.PREMIUM),
        ]
        screen = Screen("Screen-1", seats)
        movie = Movie("Inception", 148, "Sci-Fi")
        return Show("SHOW-1", movie, screen, datetime(2024, 6, 15, 19, 0))

    def test_all_seats_initially_available(self):
        show = self._make_show()
        available = show.get_available_seats()
        assert len(available) == 3

    def test_book_seats_marks_booked(self):
        show = self._make_show()
        seat = show.screen.get_seat("A1")
        show.book_seats([seat])
        assert show.get_seat_status(seat) == SeatStatus.BOOKED

    def test_book_seats_reduces_availability(self):
        show = self._make_show()
        seat = show.screen.get_seat("A1")
        show.book_seats([seat])
        available = show.get_available_seats()
        assert len(available) == 2

    def test_book_already_booked_raises(self):
        show = self._make_show()
        seat = show.screen.get_seat("A1")
        show.book_seats([seat])
        with pytest.raises(ValueError):
            show.book_seats([seat])

    def test_release_seats_restores_availability(self):
        show = self._make_show()
        seat = show.screen.get_seat("A1")
        show.book_seats([seat])
        show.release_seats([seat])
        assert show.get_seat_status(seat) == SeatStatus.AVAILABLE


class TestPhase1Booking:
    """Verify Booking creation and cancellation."""

    def _make_booking(self) -> tuple[Booking, Show]:
        seats = [
            Seat("A", 1, SeatType.REGULAR),
            Seat("A", 2, SeatType.REGULAR),
        ]
        screen = Screen("Screen-1", seats)
        movie = Movie("Inception", 148, "Sci-Fi")
        show = Show("SHOW-1", movie, screen, datetime(2024, 6, 15, 19, 0))
        seat = show.screen.get_seat("A1")
        show.book_seats([seat])
        booking = Booking("BK-0001", show, [seat], "Alice", 10.0)
        return booking, show

    def test_booking_status_confirmed(self):
        booking, _ = self._make_booking()
        assert booking.status == BookingStatus.CONFIRMED

    def test_booking_records_time(self):
        before = datetime.now()
        booking, _ = self._make_booking()
        after = datetime.now()
        assert before <= booking.booking_time <= after

    def test_cancel_booking_updates_status(self):
        booking, _ = self._make_booking()
        booking.cancel()
        assert booking.status == BookingStatus.CANCELLED

    def test_cancel_booking_releases_seats(self):
        booking, show = self._make_booking()
        booking.cancel()
        seat = show.screen.get_seat("A1")
        assert show.get_seat_status(seat) == SeatStatus.AVAILABLE


# ===================================================================
# PHASE 2: Pricing Strategies
# ===================================================================

class TestPhase2StandardPricing:
    """Verify standard seat-type-based pricing."""

    def test_regular_seats(self):
        pricing = StandardPricing(base_price=10.0)
        seats = [Seat("A", 1, SeatType.REGULAR), Seat("A", 2, SeatType.REGULAR)]
        show_time = datetime(2024, 6, 15, 14, 0)  # 2 PM
        assert pricing.calculate_price(seats, show_time) == 20.0

    def test_premium_seats(self):
        pricing = StandardPricing(base_price=10.0)
        seats = [Seat("B", 1, SeatType.PREMIUM)]
        show_time = datetime(2024, 6, 15, 14, 0)
        assert pricing.calculate_price(seats, show_time) == 15.0

    def test_vip_seats(self):
        pricing = StandardPricing(base_price=10.0)
        seats = [Seat("C", 1, SeatType.VIP)]
        show_time = datetime(2024, 6, 15, 14, 0)
        assert pricing.calculate_price(seats, show_time) == 25.0

    def test_mixed_seat_types(self):
        pricing = StandardPricing(base_price=10.0)
        seats = [
            Seat("A", 1, SeatType.REGULAR),   # 10.0
            Seat("B", 1, SeatType.PREMIUM),    # 15.0
            Seat("C", 1, SeatType.VIP),        # 25.0
        ]
        show_time = datetime(2024, 6, 15, 14, 0)
        assert pricing.calculate_price(seats, show_time) == 50.0

    def test_empty_seats_list(self):
        pricing = StandardPricing(base_price=10.0)
        show_time = datetime(2024, 6, 15, 14, 0)
        assert pricing.calculate_price([], show_time) == 0.0


class TestPhase2PeakHourPricing:
    """Verify peak-hour surcharge pricing."""

    def test_non_peak_no_surcharge(self):
        pricing = PeakHourPricing(base_price=10.0, peak_surcharge=5.0)
        seats = [Seat("A", 1, SeatType.REGULAR)]
        show_time = datetime(2024, 6, 15, 14, 0)  # 2 PM — not peak
        assert pricing.calculate_price(seats, show_time) == 10.0

    def test_peak_hour_adds_surcharge(self):
        pricing = PeakHourPricing(base_price=10.0, peak_surcharge=5.0)
        seats = [Seat("A", 1, SeatType.REGULAR)]
        show_time = datetime(2024, 6, 15, 19, 0)  # 7 PM — peak
        # 10 (base * 1.0) + 5 (surcharge) = 15
        assert pricing.calculate_price(seats, show_time) == 15.0

    def test_peak_hour_boundary_start(self):
        pricing = PeakHourPricing(base_price=10.0, peak_surcharge=5.0)
        seats = [Seat("A", 1, SeatType.REGULAR)]
        show_time = datetime(2024, 6, 15, 18, 0)  # 6 PM — peak starts
        assert pricing.calculate_price(seats, show_time) == 15.0

    def test_peak_hour_boundary_end(self):
        pricing = PeakHourPricing(base_price=10.0, peak_surcharge=5.0)
        seats = [Seat("A", 1, SeatType.REGULAR)]
        show_time = datetime(2024, 6, 15, 21, 0)  # 9 PM — peak ends
        assert pricing.calculate_price(seats, show_time) == 15.0

    def test_after_peak_no_surcharge(self):
        pricing = PeakHourPricing(base_price=10.0, peak_surcharge=5.0)
        seats = [Seat("A", 1, SeatType.REGULAR)]
        show_time = datetime(2024, 6, 15, 22, 0)  # 10 PM — after peak
        assert pricing.calculate_price(seats, show_time) == 10.0

    def test_peak_with_mixed_types(self):
        pricing = PeakHourPricing(base_price=10.0, peak_surcharge=3.0)
        seats = [
            Seat("A", 1, SeatType.REGULAR),   # 10 + 3 = 13
            Seat("C", 1, SeatType.VIP),        # 25 + 3 = 28
        ]
        show_time = datetime(2024, 6, 15, 20, 0)  # 8 PM — peak
        assert pricing.calculate_price(seats, show_time) == 41.0

    def test_peak_empty_seats(self):
        pricing = PeakHourPricing(base_price=10.0, peak_surcharge=5.0)
        show_time = datetime(2024, 6, 15, 19, 0)  # peak
        assert pricing.calculate_price([], show_time) == 0.0

    def test_peak_premium_seat(self):
        pricing = PeakHourPricing(base_price=10.0, peak_surcharge=5.0)
        seats = [Seat("B", 1, SeatType.PREMIUM)]
        show_time = datetime(2024, 6, 15, 19, 0)  # peak
        # 15 (base * 1.5) + 5 (surcharge) = 20
        assert pricing.calculate_price(seats, show_time) == 20.0


# ===================================================================
# PHASE 3: BookingSystem Integration
# ===================================================================

class TestPhase3BookingSystem:
    """Full integration tests for MovieBookingSystem."""

    def _make_system(self) -> tuple[MovieBookingSystem, Movie, Screen]:
        """Create a system with one movie and one screen."""
        pricing = StandardPricing(base_price=10.0)
        system = MovieBookingSystem(pricing_strategy=pricing)

        movie = Movie("Inception", 148, "Sci-Fi")
        system.add_movie(movie)

        seats = [
            Seat("A", 1, SeatType.REGULAR),
            Seat("A", 2, SeatType.REGULAR),
            Seat("A", 3, SeatType.REGULAR),
            Seat("B", 1, SeatType.PREMIUM),
            Seat("B", 2, SeatType.PREMIUM),
            Seat("C", 1, SeatType.VIP),
        ]
        screen = Screen("Screen-1", seats)
        system.add_screen(screen)

        return system, movie, screen

    def _schedule_show(
        self, system: MovieBookingSystem, movie: Movie, screen: Screen
    ) -> Show:
        return system.schedule_show(
            "SHOW-1", movie, screen, datetime(2024, 6, 15, 19, 0)
        )

    # --- Scheduling ---

    def test_schedule_show(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        assert show.movie is movie
        assert show.screen is screen

    # --- Searching ---

    def test_search_by_title(self):
        system, movie, screen = self._make_system()
        self._schedule_show(system, movie, screen)
        results = system.search_shows(movie_title="inception")
        assert len(results) == 1

    def test_search_by_title_partial(self):
        system, movie, screen = self._make_system()
        self._schedule_show(system, movie, screen)
        results = system.search_shows(movie_title="incep")
        assert len(results) == 1

    def test_search_by_date(self):
        system, movie, screen = self._make_system()
        self._schedule_show(system, movie, screen)
        results = system.search_shows(show_date=date(2024, 6, 15))
        assert len(results) == 1

    def test_search_by_date_no_match(self):
        system, movie, screen = self._make_system()
        self._schedule_show(system, movie, screen)
        results = system.search_shows(show_date=date(2024, 6, 16))
        assert len(results) == 0

    def test_search_no_filters_returns_all(self):
        system, movie, screen = self._make_system()
        self._schedule_show(system, movie, screen)
        results = system.search_shows()
        assert len(results) == 1

    # --- Availability ---

    def test_available_seats_initially_full(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        available = system.get_available_seats(show)
        assert len(available) == 6

    # --- Booking ---

    def test_book_seats_returns_booking(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        booking = system.book_seats(show, ["A1", "A2"], "Alice")
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.customer_name == "Alice"
        assert len(booking.seats) == 2

    def test_book_seats_calculates_price(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        booking = system.book_seats(show, ["A1", "C1"], "Bob")
        # A1 is REGULAR (10.0), C1 is VIP (25.0) → total 35.0
        assert booking.total_price == 35.0

    def test_book_seats_reduces_availability(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        system.book_seats(show, ["A1", "A2"], "Alice")
        available = system.get_available_seats(show)
        assert len(available) == 4

    def test_double_book_raises(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        system.book_seats(show, ["A1"], "Alice")
        with pytest.raises(ValueError):
            system.book_seats(show, ["A1"], "Bob")

    def test_book_invalid_seat_id_raises(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        with pytest.raises(ValueError):
            system.book_seats(show, ["Z9"], "Alice")

    # --- Cancellation ---

    def test_cancel_booking_releases_seats(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        booking = system.book_seats(show, ["A1", "A2"], "Alice")
        system.cancel_booking(booking)
        available = system.get_available_seats(show)
        assert len(available) == 6

    def test_cancel_booking_updates_status(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        booking = system.book_seats(show, ["A1"], "Alice")
        system.cancel_booking(booking)
        assert booking.status == BookingStatus.CANCELLED

    def test_cancel_already_cancelled_raises(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        booking = system.book_seats(show, ["A1"], "Alice")
        system.cancel_booking(booking)
        with pytest.raises(ValueError):
            system.cancel_booking(booking)

    def test_rebook_after_cancel(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        booking = system.book_seats(show, ["A1"], "Alice")
        system.cancel_booking(booking)
        # Now Bob can book the same seat
        booking2 = system.book_seats(show, ["A1"], "Bob")
        assert booking2.status == BookingStatus.CONFIRMED

    def test_unique_booking_ids(self):
        system, movie, screen = self._make_system()
        show = self._schedule_show(system, movie, screen)
        b1 = system.book_seats(show, ["A1"], "Alice")
        b2 = system.book_seats(show, ["A2"], "Bob")
        assert b1.booking_id != b2.booking_id
