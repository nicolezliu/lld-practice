"""
SOLUTION — Hotel Booking System

Don't peek until you've given it a solid attempt!

This is one valid solution. Yours may differ in structure and still be
perfectly correct — there's no single "right" LLD answer. Compare your
design choices against this one and think about trade-offs.

This solution uses:
- Strategy pattern for pricing (StandardPricing, WeekendPremiumPricing)
- Date-range overlap detection for preventing double-bookings
- Status-based state transitions for booking lifecycle
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import date, timedelta
from typing import Optional


# ===================================================================
# Enums
# ===================================================================

class RoomType(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    SUITE = "SUITE"


class RoomStatus(Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"


class BookingStatus(Enum):
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"


# ===================================================================
# Guest
# ===================================================================

class Guest:
    def __init__(self, name: str, email: str, phone: str = ""):
        self.name = name
        self.email = email
        self.phone = phone

    def __repr__(self) -> str:
        return f"Guest({self.name}, {self.email})"


# ===================================================================
# Room
# ===================================================================

class Room:
    def __init__(
        self,
        room_number: str,
        room_type: RoomType,
        price_per_night: float,
    ):
        self.room_number = room_number
        self.room_type = room_type
        self.price_per_night = price_per_night
        self.status = RoomStatus.AVAILABLE

    def __repr__(self) -> str:
        return (
            f"Room({self.room_number}, {self.room_type.value}, "
            f"${self.price_per_night}/night, {self.status.value})"
        )


# ===================================================================
# Booking
# ===================================================================

class Booking:
    """
    Key design decisions:

    1. Booking IDs use a simple class-level counter. In production
       you'd use UUIDs or a database sequence.

    2. Date validation happens at construction time — fail fast.

    3. The booking stores a pre-calculated total_price rather than
       computing it on the fly. The pricing strategy is applied at
       booking time by the Hotel, not by the Booking itself.
    """

    _next_id = 1

    def __init__(
        self,
        guest: Guest,
        room: Room,
        check_in_date: date,
        check_out_date: date,
        total_price: float,
    ):
        if check_out_date <= check_in_date:
            raise ValueError(
                f"Check-out date ({check_out_date}) must be after "
                f"check-in date ({check_in_date})"
            )
        self.booking_id = Booking._next_id
        Booking._next_id += 1
        self.guest = guest
        self.room = room
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.total_price = total_price
        self.status = BookingStatus.CONFIRMED

    def __repr__(self) -> str:
        return (
            f"Booking(id={self.booking_id}, guest={self.guest.name}, "
            f"room={self.room.room_number}, "
            f"{self.check_in_date} to {self.check_out_date}, "
            f"${self.total_price:.2f}, {self.status.value})"
        )


# ===================================================================
# Pricing strategies (Strategy pattern)
# ===================================================================

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(
        self,
        price_per_night: float,
        check_in: date,
        check_out: date,
    ) -> float:
        ...


class StandardPricing(PricingStrategy):
    """Flat rate — base price multiplied by number of nights."""

    def calculate_price(
        self,
        price_per_night: float,
        check_in: date,
        check_out: date,
    ) -> float:
        num_nights = (check_out - check_in).days
        return price_per_night * num_nights


class WeekendPremiumPricing(PricingStrategy):
    """
    Premium rate on Friday and Saturday nights.

    A "night" is keyed by its start date:
    - weekday() == 4 → Friday night
    - weekday() == 5 → Saturday night

    Weekend nights cost price_per_night * premium_multiplier.
    Weekday nights cost the base price_per_night.
    """

    def __init__(self, premium_multiplier: float = 1.5):
        self._multiplier = premium_multiplier

    def calculate_price(
        self,
        price_per_night: float,
        check_in: date,
        check_out: date,
    ) -> float:
        total = 0.0
        current = check_in
        while current < check_out:
            if current.weekday() in (4, 5):  # Friday, Saturday
                total += price_per_night * self._multiplier
            else:
                total += price_per_night
            current += timedelta(days=1)
        return total


# ===================================================================
# Hotel (the orchestrator)
# ===================================================================

class Hotel:
    """
    Key design decisions:

    1. Rooms are stored in a list managed by add_room(). The hotel
       doesn't create rooms — the caller does. This keeps room
       configuration flexible.

    2. Bookings are stored in a flat list. For large scale you'd
       index by room and date range for O(1) lookups, but a linear
       scan is fine for an LLD exercise.

    3. Overlap detection uses the half-open interval convention
       [check_in, check_out). This means a check-out on June 5 and
       a check-in on June 5 do NOT overlap — the room is free on
       the check-out day.

    4. The pricing strategy is injected via the constructor
       (Strategy pattern). Swap StandardPricing for
       WeekendPremiumPricing without changing any Hotel logic.
    """

    def __init__(self, name: str, pricing_strategy: PricingStrategy):
        self._name = name
        self._pricing = pricing_strategy
        self._rooms: list[Room] = []
        self._bookings: list[Booking] = []

    def add_room(self, room: Room) -> None:
        self._rooms.append(room)

    def search_available_rooms(
        self,
        check_in: date,
        check_out: date,
        room_type: Optional[RoomType] = None,
    ) -> list[Room]:
        if check_out <= check_in:
            raise ValueError("Check-out date must be after check-in date")

        available = []
        for room in self._rooms:
            # Skip rooms in maintenance
            if room.status == RoomStatus.MAINTENANCE:
                continue
            # Filter by type if specified
            if room_type is not None and room.room_type != room_type:
                continue
            # Check for overlapping active bookings
            if not self._has_overlap(room, check_in, check_out):
                available.append(room)
        return available

    def book_room(
        self,
        guest: Guest,
        room: Room,
        check_in: date,
        check_out: date,
    ) -> Booking:
        if check_out <= check_in:
            raise ValueError("Check-out date must be after check-in date")

        if self._has_overlap(room, check_in, check_out):
            raise ValueError(
                f"Room {room.room_number} is not available "
                f"from {check_in} to {check_out}"
            )

        total_price = self._pricing.calculate_price(
            room.price_per_night, check_in, check_out
        )
        booking = Booking(guest, room, check_in, check_out, total_price)
        self._bookings.append(booking)
        return booking

    def cancel_booking(self, booking: Booking) -> None:
        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError(
                f"Cannot cancel booking {booking.booking_id} — "
                f"status is {booking.status.value}"
            )
        booking.status = BookingStatus.CANCELLED

    def check_in(self, booking: Booking) -> None:
        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError(
                f"Cannot check in booking {booking.booking_id} — "
                f"status is {booking.status.value}"
            )
        booking.status = BookingStatus.CHECKED_IN
        booking.room.status = RoomStatus.OCCUPIED

    def check_out(self, booking: Booking) -> None:
        if booking.status != BookingStatus.CHECKED_IN:
            raise ValueError(
                f"Cannot check out booking {booking.booking_id} — "
                f"status is {booking.status.value}"
            )
        booking.status = BookingStatus.CHECKED_OUT
        booking.room.status = RoomStatus.AVAILABLE

    def _has_overlap(self, room: Room, check_in: date, check_out: date) -> bool:
        """
        Check if a room has any active bookings overlapping [check_in, check_out).

        Two half-open intervals [A, B) and [C, D) overlap when A < D and C < B.
        """
        for booking in self._bookings:
            if booking.room is not room:
                continue
            if booking.status in (BookingStatus.CANCELLED, BookingStatus.CHECKED_OUT):
                continue
            # Overlap check: [existing.check_in, existing.check_out) vs [check_in, check_out)
            if booking.check_in_date < check_out and check_in < booking.check_out_date:
                return True
        return False
