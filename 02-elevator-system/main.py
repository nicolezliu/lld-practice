"""
Test driver for the Elevator System.

Run this to simulate your elevator system:
    python main.py

The simulation runs step-by-step so you can trace what each elevator does.
"""

from models import Direction
from dispatcher import NearestElevatorStrategy
from elevator_system import ElevatorSystem


def main():
    print("=" * 60)
    print("ELEVATOR SYSTEM — LLD PRACTICE")
    print("=" * 60)

    # --- Setup: 10-floor building with 3 elevators ---
    strategy = NearestElevatorStrategy()
    system = ElevatorSystem(
        num_floors=10,
        num_elevators=3,
        capacity_per_elevator=8,
        dispatch_strategy=strategy,
    )

    # --- Scenario 1: Simple request ---
    print("\n--- Scenario 1: Person on floor 5 wants to go UP ---")
    system.request_elevator(floor=5, direction=Direction.UP)
    system.display()

    # Step the simulation until the elevator arrives at floor 5
    print("\nStepping simulation...")
    for i in range(10):
        system.step()
        print(f"  Step {i + 1}:")
        system.display()

    # --- Scenario 2: Multiple concurrent requests ---
    print("\n--- Scenario 2: Requests from floors 2, 7, and 9 ---")
    system.request_elevator(floor=2, direction=Direction.UP)
    system.request_elevator(floor=7, direction=Direction.DOWN)
    system.request_elevator(floor=9, direction=Direction.DOWN)

    print("\nStepping simulation...")
    for i in range(15):
        system.step()
        print(f"  Step {i + 1}:")
        system.display()

    # --- Scenario 3: Internal request (passenger selects floor) ---
    print("\n--- Scenario 3: Passenger in elevator 0 selects floor 8 ---")
    system.select_floor(elevator_id=0, floor=8)

    print("\nStepping simulation...")
    for i in range(12):
        system.step()
        print(f"  Step {i + 1}:")
        system.display()

    # --- Add your own scenarios! ---
    # Ideas:
    #   - What happens with all elevators on floor 0 and a request on floor 9?
    #   - What happens with conflicting directions (UP from floor 5, DOWN from floor 5)?
    #   - Try the ZoneBasedStrategy and compare behavior
    #   - Stress test: rapid requests on every floor


if __name__ == "__main__":
    main()
