# Hotel Booking System — LLD Practice

## Problem Statement
Design a hotel booking system that manages rooms, guests, and reservations.

## Requirements

### Functional
- The hotel has multiple rooms of different types: SINGLE, DOUBLE, SUITE
- Each room type has a different base price per night
- Guests can search for available rooms by date range and optional room type
- Guests can book a room for a date range (check-in and check-out dates)
- Guests can cancel a booking
- Guests can check in to and check out of their booked room
- Booking tracks total price calculated from the date range and pricing strategy

### Non-Functional
- No double-booking — a room cannot be booked for overlapping date ranges
- Date range validation — check-out must be after check-in, dates must be valid
- Extensible pricing model

## Suggested Design Patterns
- **Strategy** — for pricing (standard flat rate vs. weekend premium pricing)
- **Observer** — for booking notifications (e.g., confirmation emails)
- **Factory** — for room creation by type

## Your Task
1. Define the enums and data classes in `models.py`
2. Implement pricing strategies in `pricing.py`
3. Wire everything together in `hotel.py`
4. Run `main.py` to test your design end-to-end
5. Try swapping pricing strategies and see how costs change

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models — enums, Room, Guest, Booking
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: Pricing strategies
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: Hotel integration (search, book, cancel, check-in/out)
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Add a `BookingObserver` that gets notified on booking, cancellation, check-in/out
- Add seasonal pricing (holiday surcharge)
- Add room amenities (Wi-Fi, minibar) with per-amenity charges
- Add group booking (multiple rooms in a single reservation)
