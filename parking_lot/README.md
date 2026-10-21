# LLD Practice: Parking Lot (Python)

Mid-level, CoderPad-style. Suggested time: **45 to 60 minutes**.
Do not open `solution/` until you're done.

## Problem

Design a parking lot system.

1. The lot has multiple **levels**. Each level has **spots** of size `SMALL`, `MEDIUM`, or `LARGE`.
2. There are three **vehicle types**:
   - Motorcycle: fits any spot
   - Car: fits MEDIUM or LARGE
   - Truck: fits LARGE only
3. `park(vehicle)` assigns a spot and returns a **ticket** with a unique id and entry time.
4. `unpark(ticket_id)` frees the spot and returns the **fee**.
5. **Spot assignment** must be swappable. Implement two rules:
   - First available: lowest level first, then spot order
   - Best fit: smallest spot size that fits, anywhere in the lot
6. **Pricing** must be swappable. Default: hourly by vehicle type (motorcycle $1, car $2, truck $4). Partial hours round up. Minimum 1 hour.
7. Errors: lot full for this vehicle, vehicle already parked, invalid or reused ticket.
8. Queries: find a vehicle by plate, count free spots (optionally by size), check if the lot is full.

## Layout

```
starter/parking_lot/        <- YOU EDIT THESE (look for TODO)
  enums.py                  provided
  exceptions.py             provided
  models/vehicle.py         TODO
  models/parking_spot.py    TODO
  models/level.py           TODO
  models/ticket.py          provided
  strategies/spot_assignment.py   interface provided, 2 TODOs
  strategies/pricing.py           interface provided, 1 TODO
  parking_lot.py            TODO
solution/parking_lot/       sample solution (same layout)
tests/test_parking_lot.py   29 tests in 4 parts
```

## Running tests

From this folder:

```bash
python3 -m unittest -v                          # tests your code in starter/
python3 -m unittest -v tests.test_parking_lot.TestVehicleAndSpot   # one part
LLD_TARGET=solution python3 -m unittest -v      # tests the sample solution
```

In VS Code, the Testing panel (flask icon) picks up the tests automatically. It runs against `starter/`.

All 29 tests fail at first. Work through them in order:

| Part | Test class | What it checks |
| --- | --- | --- |
| 1 | `TestVehicleAndSpot` | vehicles, fit rules, spots, levels |
| 2 | `TestParkUnpark` | tickets, errors, find, counts |
| 3 | `TestAssignmentStrategies` | first available, best fit, custom strategy |
| 4 | `TestPricing` | hourly rounding, minimum, custom pricing |

## How to run it like a real interview

1. **Clarify (5 min).** Before reading the stubs, write down questions you'd ask. Examples: Multiple entrances? Reservations? Payment methods? Concurrency?
2. **Entities (5 min).** List the classes and how they relate. Compare to the layout above.
3. **Code (30 to 40 min).** Fill in the TODOs. Run tests often.
4. **Explain (5 min).** Say out loud why `ParkingLot` takes its strategies as arguments.

## Patterns in this problem

- **Strategy**: `SpotAssignmentStrategy` and `PricingStrategy`. The lot calls `find_spot()` and `calculate_fee()` without knowing which rule is behind them. New rule = new class, no edits to `ParkingLot`.
- **Factory method**: `Level.build(...)` creates spots from a simple count dict.
- **Facade**: `ParkingLot` is the single entry point that coordinates everything.
- **Dependency injection**: strategies and the clock are passed in. That's what makes the pricing tests possible with a fake clock.

SOLID in one line each:
- **S**ingle responsibility: a spot tracks occupancy, pricing computes fees, the lot coordinates.
- **O**pen/closed: add behavior by adding a strategy class, not by editing the lot.
- **L**iskov: any `Vehicle` subclass works anywhere a `Vehicle` is expected.
- **I**nterface segregation: each strategy interface has one method.
- **D**ependency inversion: `ParkingLot` depends on the abstract strategies, not concrete ones.

## Follow-ups (interviewer extensions)

Try these after the tests pass. Notice how many require editing `ParkingLot` itself. Fewer is better.

1. Add an `ElectricCar` that can only park in a new `EV` spot size.
2. Add weekend pricing: 1.5x on Saturdays and Sundays. (Hint: a decorator around another `PricingStrategy`.)
3. Add a display board per level that updates when spots change. (Observer pattern.)
4. Two entrance gates call `park()` at the same time. What breaks? Fix it with `threading.Lock`.
5. Add reservations: a spot can be held for a plate for 15 minutes.
