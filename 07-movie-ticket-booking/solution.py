"""
SOLUTION — Movie Ticket Booking System

Don't peek until you've given it a solid attempt!

This is one valid solution. Yours may differ in structure and still be
perfectly correct — there's no single "right" LLD answer. Compare your
design choices against this one and think about trade-offs.

Key design decisions:
1. Seat identity is (row, number) — seat_type doesn't affect equality.
2. Seat availability is tracked per-Show via a dict[Seat, SeatStatus],
   not on the Seat object itself. This keeps seats reusable across shows.
3. Pricing uses the Strategy pattern — swap StandardPricing for PeakHourPricing
   without changing any booking logic.
4. Booking.cancel() delegates seat release to the Show, keeping the
   invariant in one place.
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, date
from typing import Optional


# ===================================================================
# Enums
# ===================================================================

class SeatType(Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    VIP = "VIP"


class SeatStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    BLOCKED = "BLOCKED"


class BookingStatus(Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


# ===================================================================
# Seat
# ===================================================================

class Seat:
    def __init__(self, row: str, number: int, seat_type: SeatType):
        self.row = row
        self.number = number
        self.seat_type = seat_type

    @property
    def seat_id(self) -> str:
        return f"{self.row}{self.number}"

    def __repr__(self) -> str:
        return f"Seat({self.seat_id}, {self.seat_type.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Seat):
            return NotImplemented
        return self.row == other.row and self.number == other.number

    def __hash__(self) -> int:
        return hash((self.row, self.number))


# ===================================================================
# Movie
# ===================================================================

class Movie:
    def __init__(self, title: str, duration_minutes: int, genre: str):
        self.title = title
        self.duration_minutes = duration_minutes
        self.genre = genre

    def __repr__(self) -> str:
        return f"Movie({self.title!r}, {self.duration_minutes}min)"


# ===================================================================
# Screen
# ===================================================================

class Screen:
    def __init__(self, screen_id: str, seats: list[Seat]):
        self.screen_id = screen_id
        self.seats = list(seats)
        self._seat_map: dict[str, Seat] = {s.seat_id: s for s in self.seats}

    @property
    def capacity(self) -> int:
        return len(self.seats)

    def get_seat(self, seat_id: str) -> Optional[Seat]:
        return self._seat_map.get(seat_id)

    def __repr__(self) -> str:
        return f"Screen({self.screen_id}, capacity={self.capacity})"


# ===================================================================
# Show
# ===================================================================

class Show:
    """
    A show tracks seat availability independently of the screen's
    physical layout. Two shows on the same screen have separate
    availability maps.
    """

    def __init__(self, show_id: str, movie: Movie, screen: Screen, start_time: datetime):
        self.show_id = show_id
        self.movie = movie
        self.screen = screen
        self.start_time = start_time
        # Every seat starts as AVAILABLE for this show
        self._seat_status: dict[Seat, SeatStatus] = {
            seat: SeatStatus.AVAILABLE for seat in screen.seats
        }

    def get_available_seats(self) -> list[Seat]:
        return [
            seat for seat, status in self._seat_status.items()
            if status == SeatStatus.AVAILABLE
        ]

    def get_seat_status(self, seat: Seat) -> SeatStatus:
        return self._seat_status.get(seat, SeatStatus.AVAILABLE)

    def book_seats(self, seats: list[Seat]) -> None:
        # Validate all seats are available BEFORE marking any
        for seat in seats:
            status = self._seat_status.get(seat)
            if status is None:
                raise ValueError(f"Seat {seat.seat_id} does not exist in this screen")
            if status != SeatStatus.AVAILABLE:
                raise ValueError(
                    f"Seat {seat.seat_id} is {status.value}, cannot book"
                )
        # All clear — mark them booked
        for seat in seats:
            self._seat_status[seat] = SeatStatus.BOOKED

    def release_seats(self, seats: list[Seat]) -> None:
        for seat in seats:
            if seat in self._seat_status:
                self._seat_status[seat] = SeatStatus.AVAILABLE

    def __repr__(self) -> str:
        avail = len(self.get_available_seats())
        return (
            f"Show({self.show_id}, {self.movie.title!r}, "
            f"{self.screen.screen_id}, {self.start_time}, "
            f"available={avail}/{self.screen.capacity})"
        )


# ===================================================================
# Booking
# ===================================================================

class Booking:
    def __init__(
        self,
        booking_id: str,
        show: Show,
        seats: list[Seat],
        customer_name: str,
        total_price: float,
    ):
        self.booking_id = booking_id
        self.show = show
        self.seats = list(seats)
        self.customer_name = customer_name
        self.total_price = total_price
        self.status = BookingStatus.CONFIRMED
        self.booking_time = datetime.now()

    def cancel(self) -> None:
        self.status = BookingStatus.CANCELLED
        self.show.release_seats(self.seats)

    def __repr__(self) -> str:
        seat_ids = ", ".join(s.seat_id for s in self.seats)
        return (
            f"Booking({self.booking_id}, {self.customer_name!r}, "
            f"[{seat_ids}], ${self.total_price:.2f}, {self.status.value})"
        )


# ===================================================================
# Pricing strategies (Strategy pattern)
# ===================================================================

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, seats: list[Seat], show_time: datetime) -> float:
        ...


class StandardPricing(PricingStrategy):
    """
    Seat-type multipliers applied to a base price:
    - REGULAR: 1.0x
    - PREMIUM: 1.5x
    - VIP:     2.5x
    """

    MULTIPLIERS = {
        SeatType.REGULAR: 1.0,
        SeatType.PREMIUM: 1.5,
        SeatType.VIP: 2.5,
    }

    def __init__(self, base_price: float):
        self._base_price = base_price

    def calculate_price(self, seats: list[Seat], show_time: datetime) -> float:
        total = 0.0
        for seat in seats:
            multiplier = self.MULTIPLIERS.get(seat.seat_type, 1.0)
            total += self._base_price * multiplier
        return total


class PeakHourPricing(PricingStrategy):
    """
    Standard seat-type pricing + a flat per-seat surcharge during
    peak hours (18:00–21:00 inclusive).
    """

    MULTIPLIERS = {
        SeatType.REGULAR: 1.0,
        SeatType.PREMIUM: 1.5,
        SeatType.VIP: 2.5,
    }

    def __init__(self, base_price: float, peak_surcharge: float):
        self._base_price = base_price
        self._peak_surcharge = peak_surcharge

    def _is_peak(self, show_time: datetime) -> bool:
        return 18 <= show_time.hour <= 21

    def calculate_price(self, seats: list[Seat], show_time: datetime) -> float:
        total = 0.0
        is_peak = self._is_peak(show_time)
        for seat in seats:
            multiplier = self.MULTIPLIERS.get(seat.seat_type, 1.0)
            price = self._base_price * multiplier
            if is_peak:
                price += self._peak_surcharge
            total += price
        return total


# ===================================================================
# MovieBookingSystem (the orchestrator)
# ===================================================================

class MovieBookingSystem:
    """
    Key design decisions in this solution:

    1. Movies and screens are registered before scheduling shows.
       schedule_show doesn't enforce this — it's the caller's job.
       A stricter version would validate registration.

    2. Booking IDs are sequential: BK-0001, BK-0002, etc.
       In production you'd use UUIDs.

    3. search_shows supports case-insensitive partial match on title
       and exact date match. Both filters are optional and composable.

    4. book_seats validates ALL seats before marking any as BOOKED.
       This prevents partial bookings (atomic all-or-nothing).

    5. Thread safety is NOT implemented. In production, you'd need
       locking around book_seats and cancel_booking to prevent races.
    """

    def __init__(self, pricing_strategy: PricingStrategy):
        self._pricing = pricing_strategy
        self._movies: list[Movie] = []
        self._screens: list[Screen] = []
        self._shows: list[Show] = []
        self._bookings: list[Booking] = []
        self._booking_counter = 0

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def add_movie(self, movie: Movie) -> None:
        self._movies.append(movie)

    def add_screen(self, screen: Screen) -> None:
        self._screens.append(screen)

    def schedule_show(
        self,
        show_id: str,
        movie: Movie,
        screen: Screen,
        start_time: datetime,
    ) -> Show:
        show = Show(show_id, movie, screen, start_time)
        self._shows.append(show)
        return show

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def search_shows(
        self,
        movie_title: Optional[str] = None,
        show_date: Optional[date] = None,
    ) -> list[Show]:
        results = self._shows
        if movie_title is not None:
            title_lower = movie_title.lower()
            results = [
                s for s in results
                if title_lower in s.movie.title.lower()
            ]
        if show_date is not None:
            results = [
                s for s in results
                if s.start_time.date() == show_date
            ]
        return results

    def get_available_seats(self, show: Show) -> list[Seat]:
        return show.get_available_seats()

    # ------------------------------------------------------------------
    # Booking
    # ------------------------------------------------------------------

    def book_seats(
        self,
        show: Show,
        seat_ids: list[str],
        customer_name: str,
    ) -> Booking:
        # 1. Resolve seat IDs → Seat objects
        seats: list[Seat] = []
        for sid in seat_ids:
            seat = show.screen.get_seat(sid)
            if seat is None:
                raise ValueError(f"Seat '{sid}' not found in {show.screen.screen_id}")
            seats.append(seat)

        # 2. Validate all are available (Show.book_seats does this atomically)
        show.book_seats(seats)

        # 3. Calculate price
        total_price = self._pricing.calculate_price(seats, show.start_time)

        # 4. Create booking
        booking_id = self._next_booking_id()
        booking = Booking(booking_id, show, seats, customer_name, total_price)
        self._bookings.append(booking)
        return booking

    def cancel_booking(self, booking: Booking) -> None:
        if booking.status == BookingStatus.CANCELLED:
            raise ValueError(
                f"Booking {booking.booking_id} is already cancelled"
            )
        booking.cancel()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _next_booking_id(self) -> str:
        self._booking_counter += 1
        return f"BK-{self._booking_counter:04d}"
