"""
Core Movie Ticket Booking logic.

Your job: implement the MovieBookingSystem class.
This is the main entry point — it orchestrates movies, screens, shows,
and bookings.

Think about:
- How do you prevent double-booking of seats?
- How do you generate unique booking IDs?
- How do you handle cancellations?
"""

from typing import Optional
from datetime import datetime, date

from models import (
    Movie, Screen, Seat, Show, Booking,
    SeatType, SeatStatus, BookingStatus,
)
from pricing import PricingStrategy


class MovieBookingSystem:
    """
    The main booking system.

    Manages movies, screens, shows, and bookings.
    """

    def __init__(self, pricing_strategy: PricingStrategy):
        """
        Initialize the booking system with a pricing strategy.

        Think about what collections you need:
        - movies, screens, shows, bookings
        - a booking ID counter or generator
        """
        # TODO: initialize collections and pricing strategy
        pass

    # ------------------------------------------------------------------
    # Setup methods (add inventory)
    # ------------------------------------------------------------------

    def add_movie(self, movie: Movie) -> None:
        """Register a movie in the system."""
        # TODO
        pass

    def add_screen(self, screen: Screen) -> None:
        """Register a screen in the system."""
        # TODO
        pass

    def schedule_show(
        self,
        show_id: str,
        movie: Movie,
        screen: Screen,
        start_time: datetime,
    ) -> Show:
        """
        Schedule a show — a movie on a screen at a specific time.

        Returns:
            The created Show object.

        Think about:
        - Should you validate that the movie and screen are registered?
        - Should you check for scheduling conflicts (overlapping shows on same screen)?
        """
        # TODO
        pass

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    def search_shows(
        self,
        movie_title: Optional[str] = None,
        show_date: Optional[date] = None,
    ) -> list[Show]:
        """
        Search for shows, optionally filtering by movie title and/or date.

        Args:
            movie_title: filter by movie title (case-insensitive partial match)
            show_date: filter by date (matches shows on that calendar day)

        Returns:
            List of matching shows.
        """
        # TODO
        pass

    def get_available_seats(self, show: Show) -> list[Seat]:
        """Return all available seats for a given show."""
        # TODO
        pass

    # ------------------------------------------------------------------
    # Booking methods
    # ------------------------------------------------------------------

    def book_seats(
        self,
        show: Show,
        seat_ids: list[str],
        customer_name: str,
    ) -> Booking:
        """
        Book specific seats for a show.

        Args:
            show: the show to book
            seat_ids: list of seat IDs (e.g. ["A1", "A2"])
            customer_name: name of the customer

        Returns:
            A Booking object with CONFIRMED status.

        Raises:
            ValueError: if any seat ID is invalid or any seat is not available.

        Think about:
        - Look up Seat objects from IDs
        - Verify all seats are AVAILABLE before booking any
        - Calculate total price using the pricing strategy
        - Mark seats as BOOKED on the show
        - Create and store the Booking
        """
        # TODO
        pass

    def cancel_booking(self, booking: Booking) -> None:
        """
        Cancel a booking — release the seats and update booking status.

        Raises:
            ValueError: if the booking is already cancelled.
        """
        # TODO
        pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _next_booking_id(self) -> str:
        """Generate a unique booking ID."""
        # TODO: e.g. "BK-0001", "BK-0002", ...
        pass
