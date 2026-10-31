"""
Test driver for the Vending Machine system.

Run this to verify your implementation:
    python main.py

Start with the basic scenarios, then add your own edge cases.
"""

from models import Coin, Bill, Product, Inventory
from vending_machine import VendingMachine


def main():
    print("=" * 60)
    print("VENDING MACHINE — LLD PRACTICE")
    print("=" * 60)

    # --- Setup: stock the machine ---
    inv = Inventory()
    inv.add_product("A1", Product("Coca-Cola", price=150, quantity=5))
    inv.add_product("A2", Product("Sprite", price=150, quantity=3))
    inv.add_product("B1", Product("Water", price=100, quantity=10))
    inv.add_product("B2", Product("Chips", price=125, quantity=2))
    inv.add_product("C1", Product("Candy Bar", price=75, quantity=8))

    vm = VendingMachine(inv)

    # --- Scenario 1: Buy with exact change ---
    print("\n--- Scenario 1: Buy Coca-Cola ($1.50) with exact change ---")
    vm.display()
    vm.insert_money(Bill.ONE)       # $1.00
    vm.insert_money(Coin.QUARTER)   # $0.25
    vm.insert_money(Coin.QUARTER)   # $0.25 → total $1.50
    print(f"  Balance after inserting: {vm.get_balance()}c")
    vm.select_product("A1")
    change = vm.dispense()
    print(f"  Dispensed! Change: {change}c")
    vm.display()

    # --- Scenario 2: Buy with change returned ---
    print("\n--- Scenario 2: Buy Water ($1.00) with a $5 bill ---")
    vm.insert_money(Bill.FIVE)
    print(f"  Balance: {vm.get_balance()}c")
    vm.select_product("B1")
    change = vm.dispense()
    print(f"  Dispensed! Change: {change}c (${change / 100:.2f})")

    # --- Scenario 3: Cancel transaction ---
    print("\n--- Scenario 3: Insert money then cancel ---")
    vm.insert_money(Bill.ONE)
    vm.insert_money(Coin.DIME)
    print(f"  Balance before cancel: {vm.get_balance()}c")
    refund = vm.cancel()
    print(f"  Cancelled! Refund: {refund}c")
    print(f"  Balance after cancel: {vm.get_balance()}c")

    # --- Scenario 4: Try to buy out-of-stock item ---
    print("\n--- Scenario 4: Buy all Chips then try again ---")
    for i in range(2):  # Chips has quantity=2
        vm.insert_money(Bill.ONE)
        vm.insert_money(Coin.QUARTER)
        vm.select_product("B2")
        change = vm.dispense()
        print(f"  Purchase {i + 1}: Dispensed Chips, change={change}c")

    # Try to buy when out of stock
    vm.insert_money(Bill.ONE)
    vm.insert_money(Coin.QUARTER)
    try:
        vm.select_product("B2")
    except ValueError as e:
        print(f"  Purchase 3 failed: {e}")
    refund = vm.cancel()
    print(f"  Refunded: {refund}c")

    # --- Scenario 5: Insufficient funds ---
    print("\n--- Scenario 5: Try to buy with too little money ---")
    vm.insert_money(Coin.QUARTER)  # only 25c
    try:
        vm.select_product("A1")  # Coca-Cola costs 150c
    except ValueError as e:
        print(f"  Rejected: {e}")
    refund = vm.cancel()
    print(f"  Refunded: {refund}c")

    # --- Scenario 6: Multiple small coins ---
    print("\n--- Scenario 6: Buy Candy Bar (75c) with small coins ---")
    for _ in range(3):
        vm.insert_money(Coin.QUARTER)  # 3 × 25c = 75c
    vm.select_product("C1")
    change = vm.dispense()
    print(f"  Dispensed Candy Bar! Change: {change}c")

    # --- Final state ---
    print("\n--- Final Machine State ---")
    vm.display()

    # --- Add your own scenarios below! ---
    # Ideas:
    #   - What happens if you try to select a product before inserting money?
    #   - What happens if you insert money, select, then try to insert more?
    #   - Try buying every item until the machine is empty
    #   - What's the maximum change the machine can return?


if __name__ == "__main__":
    main()
