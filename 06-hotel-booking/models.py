"""
Models for the Hotel Booking system.

Your job: fill in the class bodies.
- Think about what data each class needs to hold
- Think about relationships (does a Booking OWN a Room? or just reference it?)
- Think about what should be an enum vs a class
"""

from enum import Enum
from datetime import date
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RoomType(Enum):
    """Types of hotel rooms."""
    # TODO: define members (SINGLE, DOUBLE, SUITE)
    pass


class RoomStatus(Enum):
    """Current status of a room."""
    # TODO: define members (AVAILABLE, OCCUPIED, MAINTENANCE)
    pass


class BookingStatus(Enum):
    """Status of a booking throughout its lifecycle."""
    # TODO: define members (CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED)
    pass


# ---------------------------------------------------------------------------
# Guest
# ---------------------------------------------------------------------------

class Guest:
    """
    A hotel guest.

    Think about:
    - What identifies a guest? (name, email, phone?)
    - Should guests be comparable by email?
    """

    def __init__(self, name: str, email: str, phone: str = ""):
        # TODO: store guest details
        pass

    def __repr__(self) -> str:
        # TODO: useful debug representation
        return f"Guest(...)"


# ---------------------------------------------------------------------------
# Room
# ---------------------------------------------------------------------------

class Room:
    """
    A single hotel room.

    Think about:
    - What identifies a room? (room number)
    - What state does a room have? (type, price, status)
    - Should the room know about its bookings, or should that live elsewhere?
    """

    def __init__(
        self,
        room_number: str,
        room_type: RoomType,
        price_per_night: float,
    ):
        """
        Args:
            room_number: unique room identifier (e.g., "101", "202")
            room_type: SINGLE, DOUBLE, or SUITE
            price_per_night: base nightly rate for this room
        """
        # TODO: initialize room state
        # - room_number, room_type, price_per_night
        # - status should start as AVAILABLE
        pass

    def __repr__(self) -> str:
        # TODO: useful debug representation
        return f"Room(...)"


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------

class Booking:
    """
    A reservation linking a guest to a room for a date range.

    Think about:
    - What info does a booking carry?
    - How is total_price calculated? (externally via pricing strategy)
    - What's the lifecycle? CONFIRMED → CHECKED_IN → CHECKED_OUT
    -                        CONFIRMED → CANCELLED
    """

    _next_id = 1  # simple auto-increment ID

    def __init__(
        self,
        guest: Guest,
        room: Room,
        check_in_date: date,
        check_out_date: date,
        total_price: float,
    ):
        """
        Args:
            guest: the guest making the reservation
            room: the room being booked
            check_in_date: arrival date
            check_out_date: departure date
            total_price: pre-calculated total (from pricing strategy)
        """
        # TODO: assign a booking_id (auto-increment), store all fields
        # - status should start as CONFIRMED
        # - Raise ValueError if check_out_date <= check_in_date
        pass

    def __repr__(self) -> str:
        # TODO: useful debug representation
        return f"Booking(...)"
