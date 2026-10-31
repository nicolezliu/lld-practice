"""
Test driver for the Movie Ticket Booking system.

Run this to verify your implementation:
    python main.py

Start with the basic scenarios, then add your own edge cases.
"""

from datetime import datetime, date

from models import (
    SeatType, Seat, Movie, Screen, Show, Booking,
)
from pricing import StandardPricing, PeakHourPricing
from booking_system import MovieBookingSystem


def build_screen(screen_id: str) -> Screen:
    """Helper: build a screen with 3 rows (A=REGULAR, B=PREMIUM, C=VIP), 5 seats each."""
    seats = []
    layout = [
        ("A", SeatType.REGULAR),
        ("B", SeatType.PREMIUM),
        ("C", SeatType.VIP),
    ]
    for row, seat_type in layout:
        for num in range(1, 6):
            seats.append(Seat(row, num, seat_type))
    return Screen(screen_id, seats)


def main():
    print("=" * 60)
    print("MOVIE TICKET BOOKING — LLD PRACTICE")
    print("=" * 60)

    # --- Setup ---
    pricing = StandardPricing(base_price=12.0)
    system = MovieBookingSystem(pricing_strategy=pricing)

    inception = Movie("Inception", 148, "Sci-Fi")
    avengers = Movie("Avengers: Endgame", 181, "Action")
    system.add_movie(inception)
    system.add_movie(avengers)

    screen1 = build_screen("Screen-1")
    screen2 = build_screen("Screen-2")
    system.add_screen(screen1)
    system.add_screen(screen2)

    show1 = system.schedule_show(
        "SHOW-1", inception, screen1, datetime(2024, 6, 15, 14, 0)
    )
    show2 = system.schedule_show(
        "SHOW-2", inception, screen1, datetime(2024, 6, 15, 19, 0)
    )
    show3 = system.schedule_show(
        "SHOW-3", avengers, screen2, datetime(2024, 6, 15, 20, 0)
    )

    # --- Scenario 1: Search for shows ---
    print("\n--- Scenario 1: Search shows by title ---")
    results = system.search_shows(movie_title="inception")
    for s in results:
        print(f"  {s}")

    print("\n--- Search by date ---")
    results = system.search_shows(show_date=date(2024, 6, 15))
    for s in results:
        print(f"  {s}")

    # --- Scenario 2: Book seats ---
    print("\n--- Scenario 2: Book REGULAR + VIP seats ---")
    available = system.get_available_seats(show1)
    print(f"  Available seats for {show1.show_id}: {len(available)}")

    booking1 = system.book_seats(show1, ["A1", "A2", "C1"], "Alice")
    print(f"  Booked: {booking1}")
    print(f"  Total price: ${booking1.total_price:.2f}")

    available = system.get_available_seats(show1)
    print(f"  Available seats after booking: {len(available)}")

    # --- Scenario 3: Try double-booking ---
    print("\n--- Scenario 3: Double-booking prevention ---")
    try:
        system.book_seats(show1, ["A1"], "Bob")
        print("  ERROR: Should have raised!")
    except ValueError as e:
        print(f"  Correctly prevented: {e}")

    # --- Scenario 4: Cancel and rebook ---
    print("\n--- Scenario 4: Cancel and rebook ---")
    system.cancel_booking(booking1)
    print(f"  Booking after cancel: {booking1}")

    available = system.get_available_seats(show1)
    print(f"  Available seats after cancel: {len(available)}")

    booking2 = system.book_seats(show1, ["A1", "C1"], "Bob")
    print(f"  Re-booked by Bob: {booking2}")

    # --- Scenario 5: Multiple bookings ---
    print("\n--- Scenario 5: Multiple bookings on different shows ---")
    b_alice = system.book_seats(show2, ["B1", "B2"], "Alice")
    b_charlie = system.book_seats(show3, ["C3", "C4", "C5"], "Charlie")
    print(f"  Alice on show2: {b_alice}")
    print(f"  Charlie on show3: {b_charlie}")

    # --- Scenario 6: Premium pricing ---
    print("\n--- Scenario 6: Peak-hour pricing comparison ---")
    peak_pricing = PeakHourPricing(base_price=12.0, peak_surcharge=5.0)
    peak_system = MovieBookingSystem(pricing_strategy=peak_pricing)
    peak_system.add_movie(inception)
    peak_system.add_screen(build_screen("Screen-P"))

    afternoon = peak_system.schedule_show(
        "PEAK-1", inception, peak_system._screens[0], datetime(2024, 6, 15, 14, 0)
    )
    evening = peak_system.schedule_show(
        "PEAK-2", inception, peak_system._screens[0], datetime(2024, 6, 15, 19, 0)
    )

    b_afternoon = peak_system.book_seats(afternoon, ["A1"], "Test")
    b_evening = peak_system.book_seats(evening, ["A1"], "Test")
    print(f"  Afternoon (2 PM) REGULAR seat: ${b_afternoon.total_price:.2f}")
    print(f"  Evening   (7 PM) REGULAR seat: ${b_evening.total_price:.2f}")

    # --- Add your own scenarios below! ---
    # Ideas:
    #   - Book all seats in a show — what happens when the next person tries?
    #   - Try cancelling an already-cancelled booking
    #   - Search with both title and date filters
    #   - Compare pricing for VIP seats during peak hours


if __name__ == "__main__":
    main()
