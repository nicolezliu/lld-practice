# Movie Ticket Booking System — LLD Practice

## Problem Statement
Design a movie ticket booking system that manages cinemas, screens, shows, and
seat reservations. This is directly relevant to the StubHub/ticketing domain —
think about how seat inventory, pricing tiers, and concurrent booking prevention
map to real-world marketplace challenges.

## Requirements

### Functional
- A cinema has multiple screens, each screen has a grid of seats
- Seats come in three types: REGULAR, PREMIUM, VIP — each with different pricing
- Movies can be scheduled as shows on a screen at a specific date/time
- Users can search for shows by movie title or date
- Users can view available seats for a show
- Users can book one or more seats for a show, receiving a Booking confirmation
- Users can cancel a booking, which releases the seats back to available
- Booking calculates total price based on seat types and pricing strategy

### Non-Functional
- No double-booking: once a seat is booked for a show, it cannot be booked again
- Concurrent booking handling (seat locking / blocking)
- Efficient seat availability lookup

## Suggested Design Patterns
- **Strategy** — for pricing (standard vs peak-hour vs promotional)
- **Observer** — for booking notifications (email confirmation, analytics, etc.)
- **Factory** — for seat creation (building a screen's seat grid)

## Your Task
1. Fill in the class bodies in `models.py`
2. Implement the pricing strategies in `pricing.py`
3. Implement the booking logic in `booking_system.py`
4. Run `main.py` to test your design end-to-end
5. Add your own test scenarios in `main.py`

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models — enums, seats, movies, screens, shows, bookings
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: Pricing strategies
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: BookingSystem integration (search, book, cancel, double-book prevention)
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Add a coupon/discount system (percentage off, flat amount off, BOGO)
- Add a waiting list for sold-out shows
- Add a seat-hold/expiry mechanism (seats blocked for 5 minutes during checkout)
- Add screen formats (IMAX, 3D, Standard) with pricing modifiers
