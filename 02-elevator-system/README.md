# Elevator System — LLD Practice

## Problem Statement
Design an elevator system for a building with multiple elevators and floors.

## Requirements

### Functional
- Building has N floors and M elevators
- Users can request an elevator from any floor (specifying UP or DOWN direction)
- Users inside an elevator can select a destination floor
- Elevators move one floor at a time, stopping when there are requests for that floor
- Each elevator has a capacity (max number of people)
- Display the current floor and direction on each elevator

### Non-Functional
- Efficient dispatching — minimize wait time
- Handle concurrent requests
- Extensible scheduling algorithm

## Suggested Design Patterns
- **Strategy** — for the elevator scheduling/dispatching algorithm
- **State** — for elevator states (IDLE, MOVING_UP, MOVING_DOWN, DOOR_OPEN)
- **Observer** — for notifying displays when elevator state changes
- **Command** — for encapsulating floor requests

## Your Task
1. Define the elevator states and transitions in `models.py`
2. Implement the dispatching logic in `dispatcher.py`
3. Wire it all together in `elevator_system.py`
4. Run `main.py` to simulate the system
5. Try swapping dispatching strategies and see how behavior changes

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models — enums, elevator state machine, requests
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: Dispatcher strategies
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: ElevatorSystem integration (full simulation)
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Add an emergency stop feature
- Add priority floors (e.g., lobby gets priority)
- Implement a "SCAN" (elevator algorithm) dispatcher
- Add weight-based capacity instead of person count
