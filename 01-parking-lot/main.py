"""
Test driver for the Parking Lot system.

Run this to verify your implementation:
    python main.py

Start with the basic scenarios, then add your own edge cases.
"""

from models import Car, Motorcycle, Truck, SpotSize
from parking_lot import ParkingLot
from pricing import HourlyPricing, TieredPricing
from datetime import datetime, timedelta
import time


def main():
    print("=" * 60)
    print("PARKING LOT — LLD PRACTICE")
    print("=" * 60)

    # --- Setup ---
    pricing = HourlyPricing(rate_per_hour=2.0)
    lot = ParkingLot(
        name="Downtown Garage",
        num_floors=2,
        spots_per_floor={SpotSize.SMALL: 5, SpotSize.MEDIUM: 10, SpotSize.LARGE: 3},
        pricing_strategy=pricing,
    )

    # --- Scenario 1: Park and unpark a car ---
    print("\n--- Scenario 1: Park and unpark a car ---")
    car = Car("ABC-1234")
    ticket = lot.park_vehicle(car)
    if ticket:
        print(f"Car parked! Ticket issued at {ticket.entry_time}")
    else:
        print("ERROR: Could not park car")

    print(f"Available spots: {lot.get_available_spots()}")

    # Simulate some time passing (in real implementation, fee would be tiny)
    fee = lot.unpark_vehicle(car)
    print(f"Car unparked. Fee: ${fee:.2f}")
    print(f"Available spots after exit: {lot.get_available_spots()}")

    # --- Scenario 2: Park multiple vehicle types ---
    print("\n--- Scenario 2: Mixed vehicles ---")
    moto = Motorcycle("MOTO-001")
    truck = Truck("TRUCK-XL")
    car2 = Car("DEF-5678")

    for v in [moto, truck, car2]:
        ticket = lot.park_vehicle(v)
        status = "Parked" if ticket else "FULL"
        print(f"  {v.__class__.__name__} ({v.license_plate}): {status}")

    print(f"Available spots: {lot.get_available_spots()}")

    # --- Scenario 3: Try to park when no suitable spot exists ---
    print("\n--- Scenario 3: Fill up LARGE spots ---")
    trucks = []
    for i in range(10):  # more trucks than LARGE spots
        t = Truck(f"TRUCK-{i:03d}")
        ticket = lot.park_vehicle(t)
        if ticket:
            trucks.append(t)
            print(f"  Truck {t.license_plate}: Parked")
        else:
            print(f"  Truck {t.license_plate}: No spot available!")

    # --- Scenario 4: Unpark all and verify spots restored ---
    print("\n--- Scenario 4: Unpark everything ---")
    for v in [moto, truck, car2] + trucks:
        try:
            fee = lot.unpark_vehicle(v)
            print(f"  {v.license_plate} unparked, fee: ${fee:.2f}")
        except ValueError as e:
            print(f"  {v.license_plate} error: {e}")

    print(f"Final available spots: {lot.get_available_spots()}")

    # --- Add your own scenarios below! ---
    # Ideas:
    #   - What happens if you unpark a vehicle that isn't in the lot?
    #   - What happens if you park the same vehicle twice?
    #   - Try the TieredPricing strategy
    #   - Check per-floor availability


if __name__ == "__main__":
    main()
