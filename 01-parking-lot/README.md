# Parking Lot System — LLD Practice

## Problem Statement
Design a parking lot system that can manage vehicles parking in a multi-floor lot.

## Requirements

### Functional
- The parking lot has multiple floors, each floor has multiple spots
- Spots come in different sizes: SMALL, MEDIUM, LARGE
- Vehicle types: Motorcycle, Car, Truck
  - Motorcycle → fits in SMALL, MEDIUM, or LARGE
  - Car → fits in MEDIUM or LARGE
  - Truck → fits in LARGE only
- A vehicle entering gets a ticket with entry time
- On exit, the fee is calculated based on duration
- The system should track available spots per floor and per size

### Non-Functional
- Thread-safe (multiple entry/exit points)
- Efficient spot lookup

## Suggested Design Patterns
- **Strategy** — for pricing (hourly, flat rate, etc.)
- **Singleton** — for the ParkingLot instance
- **Factory** — for creating spots/vehicles

## Your Task
1. Fill in the class bodies in `models.py`
2. Implement the parking logic in `parking_lot.py`
3. Implement a pricing strategy in `pricing.py`
4. Run `main.py` to test your design end-to-end
5. Add your own test scenarios in `main.py`

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models — enums, vehicles, spots, tickets
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: Pricing strategies
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: ParkingLot integration (everything wired together)
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Add a `ParkingSpotObserver` that gets notified when spots free up
- Add reserved/handicapped spot types
- Add an entry/exit gate abstraction
