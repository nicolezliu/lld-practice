"""
Models for the Movie Ticket Booking system.

Your job: fill in the class bodies.
- Think about what data each class needs to hold
- Think about relationships (does a Screen OWN seats? does a Show reference a Screen?)
- Think about what should be an enum vs a class vs a dataclass
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SeatType(Enum):
    """Types of seats with different pricing tiers."""
    # TODO: define members (REGULAR, PREMIUM, VIP)
    pass


class SeatStatus(Enum):
    """Current status of a seat for a particular show."""
    # TODO: define members (AVAILABLE, BOOKED, BLOCKED)
    pass


class BookingStatus(Enum):
    """Status of a booking."""
    # TODO: define members (CONFIRMED, CANCELLED)
    pass


# ---------------------------------------------------------------------------
# Seat
# ---------------------------------------------------------------------------

class Seat:
    """
    A single seat in a screen.

    Think about:
    - What identifies a seat? (row + number)
    - What type of seat is it? (affects pricing)
    - Status is per-show, not per-seat — how do you model that?
      (Hint: the seat object itself can be stateless w.r.t. shows;
       availability is tracked at the Show level)
    """

    def __init__(self, row: str, number: int, seat_type: SeatType):
        """
        Args:
            row: row label (e.g. "A", "B", "C")
            number: seat number within the row (e.g. 1, 2, 3)
            seat_type: REGULAR, PREMIUM, or VIP
        """
        # TODO: store row, number, seat_type
        pass

    @property
    def seat_id(self) -> str:
        """Unique identifier like 'A1', 'B5', 'C12'."""
        # TODO: return f"{row}{number}"
        pass

    def __repr__(self) -> str:
        # TODO: useful debug representation
        return f"Seat(...)"

    def __eq__(self, other) -> bool:
        # TODO: seats are equal if same row and number
        pass

    def __hash__(self) -> int:
        # TODO: needed for using seats in sets/dicts
        pass


# ---------------------------------------------------------------------------
# Movie
# ---------------------------------------------------------------------------

class Movie:
    """
    A movie that can be shown on screens.

    Think about:
    - What identifies a movie?
    - What metadata does it carry?
    """

    def __init__(self, title: str, duration_minutes: int, genre: str):
        # TODO: store title, duration_minutes, genre
        pass

    def __repr__(self) -> str:
        # TODO
        return f"Movie(...)"


# ---------------------------------------------------------------------------
# Screen
# ---------------------------------------------------------------------------

class Screen:
    """
    A screen/auditorium in a cinema.

    Think about:
    - A screen has a fixed set of seats (its layout doesn't change per show)
    - How do you build the seat grid? (rows × seats_per_row)
    - Different rows might have different seat types
    """

    def __init__(self, screen_id: str, seats: list[Seat]):
        """
        Args:
            screen_id: unique identifier (e.g. "Screen-1")
            seats: list of all seats in this screen
        """
        # TODO: store screen_id, seats, compute capacity
        pass

    @property
    def capacity(self) -> int:
        """Total number of seats in this screen."""
        # TODO
        pass

    def get_seat(self, seat_id: str) -> Optional[Seat]:
        """
        Look up a seat by its ID (e.g. "A1").
        Return None if not found.
        """
        # TODO
        pass

    def __repr__(self) -> str:
        # TODO
        return f"Screen(...)"


# ---------------------------------------------------------------------------
# Show
# ---------------------------------------------------------------------------

class Show:
    """
    A specific showing of a movie on a screen at a given time.

    Think about:
    - A show links a movie to a screen at a specific datetime
    - Seat availability is per-show (same screen, different shows = independent)
    - How do you track which seats are booked for THIS show?
    """

    def __init__(self, show_id: str, movie: Movie, screen: Screen, start_time: datetime):
        """
        Args:
            show_id: unique identifier
            movie: the movie being shown
            screen: the screen/auditorium
            start_time: when the show starts
        """
        # TODO: store fields
        # TODO: initialize seat status tracking (all seats start AVAILABLE)
        pass

    def get_available_seats(self) -> list[Seat]:
        """Return all seats that are currently AVAILABLE for this show."""
        # TODO
        pass

    def get_seat_status(self, seat: Seat) -> SeatStatus:
        """Return the booking status of a specific seat for this show."""
        # TODO
        pass

    def book_seats(self, seats: list[Seat]) -> None:
        """
        Mark seats as BOOKED for this show.
        Raise ValueError if any seat is not AVAILABLE.
        """
        # TODO
        pass

    def release_seats(self, seats: list[Seat]) -> None:
        """
        Release seats back to AVAILABLE (used when cancelling a booking).
        """
        # TODO
        pass

    def __repr__(self) -> str:
        # TODO
        return f"Show(...)"


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------

class Booking:
    """
    A confirmed booking — links a customer to seats for a show.

    Think about:
    - What info does a booking carry?
    - How is total price calculated? (delegated to pricing strategy)
    - What happens on cancellation?
    """

    def __init__(
        self,
        booking_id: str,
        show: Show,
        seats: list[Seat],
        customer_name: str,
        total_price: float,
    ):
        # TODO: store all fields, set status to CONFIRMED, record booking_time
        pass

    def cancel(self) -> None:
        """
        Cancel this booking.
        
        Think about:
        - Update the booking status
        - Release the seats on the show
        """
        # TODO
        pass

    def __repr__(self) -> str:
        # TODO
        return f"Booking(...)"
