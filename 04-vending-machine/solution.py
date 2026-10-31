"""
SOLUTION — Vending Machine System

Don't peek until you've given it a solid attempt!

This solution uses:
- State pattern for machine states (IdleState, HasMoneyState, DispensingState)
- All money in cents to avoid floating-point issues
- Clean separation between context (VendingMachine) and behavior (states)

Compare your design choices — there's no single right answer.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union


# ===================================================================
# Enums — money types
# ===================================================================

class Coin(Enum):
    PENNY = 1
    NICKEL = 5
    DIME = 10
    QUARTER = 25


class Bill(Enum):
    ONE = 100
    FIVE = 500


# ===================================================================
# Product
# ===================================================================

class Product:
    """
    Key design decisions:

    1. Price is in cents — avoids floating-point arithmetic entirely.
       $1.50 is stored as 150.

    2. Quantity is tracked per-product, not per-slot. This keeps the
       model simple; a slot is just a label pointing to a Product.
    """

    def __init__(self, name: str, price: int, quantity: int = 0):
        if price <= 0:
            raise ValueError(f"Price must be positive, got {price}")
        self.name = name
        self.price = price
        self.quantity = quantity

    def is_available(self) -> bool:
        return self.quantity > 0

    def dispense_one(self) -> None:
        if not self.is_available():
            raise ValueError(f"{self.name} is out of stock")
        self.quantity -= 1

    def restock(self, amount: int) -> None:
        self.quantity += amount

    def __repr__(self) -> str:
        return f"Product({self.name}, ${self.price / 100:.2f}, qty={self.quantity})"


# ===================================================================
# Inventory
# ===================================================================

class Inventory:
    """
    Maps slot codes (e.g. "A1", "B2") to Product instances.

    Key design decision: slots are immutable once assigned. To replace
    a product in a slot you'd need an admin interface (stretch goal).
    """

    def __init__(self):
        self._slots: dict[str, Product] = {}

    def add_product(self, slot: str, product: Product) -> None:
        if slot in self._slots:
            raise ValueError(f"Slot {slot} is already occupied")
        self._slots[slot] = product

    def get_product(self, slot: str) -> Product:
        if slot not in self._slots:
            raise KeyError(f"No product in slot {slot}")
        return self._slots[slot]

    def has_slot(self, slot: str) -> bool:
        return slot in self._slots

    def list_slots(self) -> list[str]:
        return sorted(self._slots.keys())

    def __repr__(self) -> str:
        items = ", ".join(
            f"{slot}: {prod.name}" for slot, prod in sorted(self._slots.items())
        )
        return f"Inventory({items})"


# ===================================================================
# State pattern — abstract base + concrete states
# ===================================================================

class VendingMachineState(ABC):
    """Abstract base class for vending machine states."""

    def __init__(self, machine: VendingMachine):
        self._machine = machine

    @abstractmethod
    def insert_money(self, amount: int) -> None:
        ...

    @abstractmethod
    def select_product(self, slot: str) -> None:
        ...

    @abstractmethod
    def dispense(self) -> int:
        ...

    @abstractmethod
    def cancel(self) -> int:
        ...


class IdleState(VendingMachineState):
    """Machine is idle — waiting for money."""

    def insert_money(self, amount: int) -> None:
        self._machine.add_to_balance(amount)
        self._machine.set_state(HasMoneyState(self._machine))

    def select_product(self, slot: str) -> None:
        raise RuntimeError("Insert money before selecting a product")

    def dispense(self) -> int:
        raise RuntimeError("Nothing to dispense — insert money and select a product")

    def cancel(self) -> int:
        return 0


class HasMoneyState(VendingMachineState):
    """Money inserted — waiting for product selection."""

    def insert_money(self, amount: int) -> None:
        self._machine.add_to_balance(amount)

    def select_product(self, slot: str) -> None:
        inv = self._machine.inventory
        if not inv.has_slot(slot):
            raise ValueError(f"Slot {slot} does not exist")
        product = inv.get_product(slot)
        if not product.is_available():
            raise ValueError(f"{product.name} is out of stock")
        if self._machine.get_balance() < product.price:
            raise ValueError(
                f"Insufficient funds: balance={self._machine.get_balance()}, "
                f"price={product.price}"
            )
        self._machine.set_selected_slot(slot)
        self._machine.set_state(DispensingState(self._machine))

    def dispense(self) -> int:
        raise RuntimeError("Select a product before dispensing")

    def cancel(self) -> int:
        refund = self._machine.reset_balance()
        self._machine.set_state(IdleState(self._machine))
        return refund


class DispensingState(VendingMachineState):
    """Product selected and paid for — ready to dispense."""

    def insert_money(self, amount: int) -> None:
        raise RuntimeError("Cannot insert money while dispensing")

    def select_product(self, slot: str) -> None:
        raise RuntimeError("Cannot select a product while dispensing")

    def dispense(self) -> int:
        slot = self._machine.get_selected_slot()
        product = self._machine.inventory.get_product(slot)
        product.dispense_one()
        self._machine.add_to_balance(-product.price)
        change = self._machine.reset_balance()
        self._machine.set_selected_slot(None)
        self._machine.set_state(IdleState(self._machine))
        return change

    def cancel(self) -> int:
        raise RuntimeError("Cannot cancel while dispensing")


# ===================================================================
# VendingMachine — the Context
# ===================================================================

class VendingMachine:
    """
    The vending machine — context for the State pattern.

    Key design decisions:

    1. Balance is in cents. All arithmetic is integer — no floats.

    2. The state objects mutate the machine via its public helper
       methods (add_to_balance, reset_balance, set_state, etc.).
       This keeps state logic in the state classes while the machine
       owns the data.

    3. selected_slot is set by HasMoneyState and consumed by
       DispensingState. It's cleared after dispensing.
    """

    def __init__(self, inventory: Inventory):
        self._inventory = inventory
        self._balance: int = 0
        self._selected_slot: Optional[str] = None
        self._state: VendingMachineState = IdleState(self)

    # -- State management --

    def set_state(self, state: VendingMachineState) -> None:
        self._state = state

    # -- Balance management --

    def get_balance(self) -> int:
        return self._balance

    def add_to_balance(self, amount: int) -> None:
        self._balance += amount

    def reset_balance(self) -> int:
        old = self._balance
        self._balance = 0
        return old

    # -- Slot selection --

    def set_selected_slot(self, slot: Optional[str]) -> None:
        self._selected_slot = slot

    def get_selected_slot(self) -> Optional[str]:
        return self._selected_slot

    # -- Public API (delegated to state) --

    def insert_money(self, money: Union[Coin, Bill]) -> None:
        self._state.insert_money(money.value)

    def select_product(self, slot: str) -> None:
        self._state.select_product(slot)

    def dispense(self) -> int:
        return self._state.dispense()

    def cancel(self) -> int:
        return self._state.cancel()

    @property
    def inventory(self) -> Inventory:
        return self._inventory

    def display(self) -> None:
        state_name = self._state.__class__.__name__
        print(f"  State: {state_name}")
        print(f"  Balance: {self._balance}c (${self._balance / 100:.2f})")
        print(f"  Selected slot: {self._selected_slot or 'none'}")
        print(f"  Products:")
        for slot in self._inventory.list_slots():
            p = self._inventory.get_product(slot)
            status = f"qty={p.quantity}" if p.is_available() else "OUT OF STOCK"
            print(f"    [{slot}] {p.name:<15} ${p.price / 100:.2f}  ({status})")
