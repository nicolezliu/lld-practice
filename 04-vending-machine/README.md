# Vending Machine — LLD Practice

## Problem Statement
Design a vending machine that sells products. The machine accepts coins and
bills, tracks inventory, dispenses products, and makes change.

## Requirements

### Functional
- The machine holds products in slots (e.g. "A1", "A2", "B1"), each with a name, price (in cents), and quantity
- Accepts coins: PENNY (1c), NICKEL (5c), DIME (10c), QUARTER (25c)
- Accepts bills: ONE ($1), FIVE ($5)
- User inserts money, selects a product, machine dispenses and returns change
- User can cancel a transaction and get a full refund
- Machine tracks inventory and rejects purchases when out of stock
- Machine rejects purchases when insufficient funds are inserted

### Non-Functional
- Handle edge cases: insufficient funds, out of stock, unable to make change
- Clean state transitions (no partial dispenses)
- Extensible to new payment methods

## Suggested Design Patterns
- **State** — for machine states (IDLE, HAS_MONEY, DISPENSING). Each state handles
  `insert_money`, `select_product`, `dispense`, and `cancel` differently.
- **Strategy** — for payment handling (could swap coin-based for card-based)

## Your Task
1. Define the models (coins, bills, products, inventory) in `models.py`
2. Implement the state classes in `states.py`
3. Wire the vending machine context in `vending_machine.py`
4. Run `main.py` to test your design end-to-end
5. Add your own edge-case scenarios in `main.py`

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models — enums, products, inventory
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: State transitions
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: VendingMachine integration (full buy/cancel/change flow)
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Add a `CardPayment` strategy alongside coin/bill payment
- Track the machine's internal coin/bill reserves for making change
- Add an admin/restock interface with authentication
- Add an `Observer` that logs every state transition for auditing
