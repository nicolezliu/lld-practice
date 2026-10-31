"""
Test driver for the Hotel Booking system.

Run this to verify your implementation:
    python main.py

Start with the basic scenarios, then add your own edge cases.
"""

from models import Room, Guest, RoomType, RoomStatus, BookingStatus
from hotel import Hotel
from pricing import StandardPricing, WeekendPremiumPricing
from datetime import date


def main():
    print("=" * 60)
    print("HOTEL BOOKING SYSTEM — LLD PRACTICE")
    print("=" * 60)

    # --- Setup ---
    pricing = StandardPricing()
    hotel = Hotel("Grand Hotel", pricing)
    hotel.add_room(Room("101", RoomType.SINGLE, 100.0))
    hotel.add_room(Room("102", RoomType.SINGLE, 100.0))
    hotel.add_room(Room("201", RoomType.DOUBLE, 150.0))
    hotel.add_room(Room("202", RoomType.DOUBLE, 150.0))
    hotel.add_room(Room("301", RoomType.SUITE, 300.0))

    # --- Scenario 1: Search and book a room ---
    print("\n--- Scenario 1: Search and book a room ---")
    check_in = date(2025, 7, 1)
    check_out = date(2025, 7, 4)
    available = hotel.search_available_rooms(check_in, check_out)
    print(f"Available rooms for Jul 1-4: {len(available)}")
    for r in available:
        print(f"  {r}")

    guest = Guest("Alice Smith", "alice@example.com", "555-1234")
    booking = hotel.book_room(guest, available[0], check_in, check_out)
    print(f"\nBooked: {booking}")

    # --- Scenario 2: Check availability after booking ---
    print("\n--- Scenario 2: Check availability after booking ---")
    available = hotel.search_available_rooms(check_in, check_out)
    print(f"Available rooms for Jul 1-4: {len(available)}")

    # --- Scenario 3: Search by room type ---
    print("\n--- Scenario 3: Search by room type ---")
    suites = hotel.search_available_rooms(
        check_in, check_out, room_type=RoomType.SUITE
    )
    print(f"Available suites for Jul 1-4: {len(suites)}")

    # --- Scenario 4: Check in and check out ---
    print("\n--- Scenario 4: Check in and check out ---")
    hotel.check_in(booking)
    print(f"After check-in: {booking}")
    print(f"Room status: {booking.room.status}")

    hotel.check_out(booking)
    print(f"After check-out: {booking}")
    print(f"Room status: {booking.room.status}")

    # --- Scenario 5: Cancel a booking ---
    print("\n--- Scenario 5: Cancel a booking ---")
    guest2 = Guest("Bob Jones", "bob@example.com")
    booking2 = hotel.book_room(guest2, available[1], check_in, check_out)
    print(f"Booked: {booking2}")
    hotel.cancel_booking(booking2)
    print(f"After cancel: {booking2}")

    # Verify the room is available again
    available = hotel.search_available_rooms(check_in, check_out)
    print(f"Available rooms after cancel: {len(available)}")

    # --- Scenario 6: Double-booking prevention ---
    print("\n--- Scenario 6: Double-booking prevention ---")
    suite = hotel.search_available_rooms(
        check_in, check_out, room_type=RoomType.SUITE
    )[0]
    guest3 = Guest("Carol White", "carol@example.com")
    hotel.book_room(guest3, suite, check_in, check_out)
    print(f"Suite booked for Carol: Jul 1-4")

    try:
        guest4 = Guest("Dave Black", "dave@example.com")
        hotel.book_room(guest4, suite, date(2025, 7, 2), date(2025, 7, 5))
        print("ERROR: Should have raised ValueError!")
    except ValueError as e:
        print(f"Double-booking prevented: {e}")

    # --- Scenario 7: Weekend premium pricing ---
    print("\n--- Scenario 7: Weekend premium pricing ---")
    weekend_hotel = Hotel("Weekend Hotel", WeekendPremiumPricing(1.5))
    weekend_hotel.add_room(Room("W1", RoomType.DOUBLE, 200.0))

    # Thu Jun 5 to Mon Jun 9, 2025
    # Thu(200) + Fri(300) + Sat(300) + Sun(200) = 1000
    guest5 = Guest("Eve Green", "eve@example.com")
    room = weekend_hotel.search_available_rooms(
        date(2025, 6, 5), date(2025, 6, 9)
    )[0]
    booking5 = weekend_hotel.book_room(
        guest5, room, date(2025, 6, 5), date(2025, 6, 9)
    )
    print(f"Weekend stay: {booking5}")
    print(f"Total price (with weekend premium): ${booking5.total_price:.2f}")

    # --- Add your own scenarios below! ---
    # Ideas:
    #   - What happens if you try to check in a cancelled booking?
    #   - What happens with adjacent bookings (check-out day = check-in day)?
    #   - Try putting a room in MAINTENANCE and searching for it
    #   - Book all rooms and verify search returns empty list


if __name__ == "__main__":
    main()
