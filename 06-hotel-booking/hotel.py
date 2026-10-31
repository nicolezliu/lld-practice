"""
Core Hotel logic.

Your job: implement the Hotel class.
This is the main entry point — it orchestrates rooms, bookings, and pricing.

Think about:
- How do you efficiently find available rooms for a date range?
- How do you prevent double-booking?
- How do you handle check-in/out state transitions?
"""

from datetime import date
from typing import Optional
from models import Room, Guest, Booking, RoomType, RoomStatus, BookingStatus
from pricing import PricingStrategy


class Hotel:
    """
    The main hotel booking system.

    Manages rooms, bookings, and pricing.
    """

    def __init__(self, name: str, pricing_strategy: PricingStrategy):
        """
        Args:
            name: name of the hotel
            pricing_strategy: the pricing strategy to use for cost calculation
        """
        # TODO: store hotel name, pricing strategy
        # TODO: initialize rooms list and bookings list
        pass

    def add_room(self, room: Room) -> None:
        """Add a room to the hotel."""
        # TODO
        pass

    def search_available_rooms(
        self,
        check_in: date,
        check_out: date,
        room_type: Optional[RoomType] = None,
    ) -> list[Room]:
        """
        Find rooms available for the given date range.

        A room is available if:
        - Its status is not MAINTENANCE
        - It has no CONFIRMED or CHECKED_IN bookings that overlap the date range

        Two date ranges [A, B) and [C, D) overlap when A < D and C < B.

        Args:
            check_in: desired check-in date
            check_out: desired check-out date
            room_type: optional filter by room type

        Returns:
            List of available rooms.
        """
        # TODO:
        # 1. Validate dates (check_out must be after check_in)
        # 2. Filter rooms by type (if specified)
        # 3. Exclude rooms with overlapping active bookings
        # 4. Exclude rooms in MAINTENANCE status
        pass

    def book_room(
        self,
        guest: Guest,
        room: Room,
        check_in: date,
        check_out: date,
    ) -> Booking:
        """
        Book a room for a guest.

        Raises:
            ValueError: if the room is not available for the given dates.
            ValueError: if check_out <= check_in.

        Returns:
            The created Booking.
        """
        # TODO:
        # 1. Validate dates
        # 2. Check room is available (no overlapping bookings)
        # 3. Calculate price using pricing strategy
        # 4. Create and store a Booking
        # 5. Return the booking
        pass

    def cancel_booking(self, booking: Booking) -> None:
        """
        Cancel a booking.

        Only CONFIRMED bookings can be cancelled.

        Raises:
            ValueError: if the booking is not in CONFIRMED status.
        """
        # TODO: update booking status to CANCELLED
        pass

    def check_in(self, booking: Booking) -> None:
        """
        Check in a guest.

        Only CONFIRMED bookings can be checked in.
        Sets the room status to OCCUPIED.

        Raises:
            ValueError: if the booking is not in CONFIRMED status.
        """
        # TODO:
        # 1. Validate booking status is CONFIRMED
        # 2. Update booking status to CHECKED_IN
        # 3. Update room status to OCCUPIED
        pass

    def check_out(self, booking: Booking) -> None:
        """
        Check out a guest.

        Only CHECKED_IN bookings can be checked out.
        Sets the room status back to AVAILABLE.

        Raises:
            ValueError: if the booking is not in CHECKED_IN status.
        """
        # TODO:
        # 1. Validate booking status is CHECKED_IN
        # 2. Update booking status to CHECKED_OUT
        # 3. Update room status to AVAILABLE
        pass

    def _has_overlap(self, room: Room, check_in: date, check_out: date) -> bool:
        """
        Check if a room has any active bookings overlapping the date range.

        Active bookings are those with status CONFIRMED or CHECKED_IN.
        Two ranges [A, B) and [C, D) overlap when A < D and C < B.
        """
        # TODO
        pass
