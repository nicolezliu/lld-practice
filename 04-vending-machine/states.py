"""
State classes for the Vending Machine (State pattern).

Your job: implement each state so transitions are handled cleanly.

The State pattern means:
- The VendingMachine (context) delegates behavior to its current state object.
- Each state decides what happens for insert_money, select_product, dispense, cancel.
- States transition the machine to a new state when appropriate.

Think about:
- What should happen if you try to select a product before inserting money?
- What should happen if you insert more money when you've already inserted some?
- What should happen if you cancel while dispensing?

Key rule: every state method should either perform the action OR raise an
appropriate error — never silently ignore.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular import — only used for type hints
    from vending_machine import VendingMachine


class VendingMachineState(ABC):
    """
    Abstract base class for vending machine states.

    Each concrete state receives a reference to the VendingMachine (the context)
    so it can read balance, inventory, and trigger state transitions.
    """

    def __init__(self, machine: VendingMachine):
        # TODO: store reference to the machine context
        pass

    @abstractmethod
    def insert_money(self, amount: int) -> None:
        """
        Handle money insertion.

        Args:
            amount: value in cents (comes from Coin.value or Bill.value)
        """
        ...

    @abstractmethod
    def select_product(self, slot: str) -> None:
        """
        Handle product selection.

        Args:
            slot: the slot code (e.g. "A1")
        """
        ...

    @abstractmethod
    def dispense(self) -> int:
        """
        Dispense the selected product and return change in cents.

        Returns:
            The change to return (in cents).
        """
        ...

    @abstractmethod
    def cancel(self) -> int:
        """
        Cancel the transaction and return inserted money.

        Returns:
            The refund amount (in cents).
        """
        ...


# ---------------------------------------------------------------------------
# Concrete states
# ---------------------------------------------------------------------------

class IdleState(VendingMachineState):
    """
    Machine is idle — waiting for money.

    Valid actions: insert_money, cancel (no-op, returns 0)
    Invalid actions: select_product (no money), dispense (nothing selected)
    """

    def insert_money(self, amount: int) -> None:
        """
        Accept money and transition to HasMoneyState.
        """
        # TODO:
        # 1. Add amount to the machine's balance
        # 2. Transition to HasMoneyState
        pass

    def select_product(self, slot: str) -> None:
        """Raise error — must insert money first."""
        # TODO: raise an appropriate error
        pass

    def dispense(self) -> int:
        """Raise error — nothing to dispense."""
        # TODO: raise an appropriate error
        pass

    def cancel(self) -> int:
        """No-op — nothing to refund."""
        # TODO: return 0
        pass


class HasMoneyState(VendingMachineState):
    """
    Money has been inserted — waiting for product selection.

    Valid actions: insert_money (add more), select_product, cancel (refund)
    Invalid actions: dispense (no product selected yet)
    """

    def insert_money(self, amount: int) -> None:
        """Accept more money — stay in HasMoneyState."""
        # TODO: add to balance
        pass

    def select_product(self, slot: str) -> None:
        """
        Select a product. Validate stock and funds, then transition to DispensingState.

        Raise ValueError if:
        - Slot doesn't exist
        - Product is out of stock
        - Insufficient funds
        """
        # TODO:
        # 1. Check slot exists
        # 2. Check product is in stock
        # 3. Check balance >= price
        # 4. Store the selected slot on the machine
        # 5. Transition to DispensingState
        pass

    def dispense(self) -> int:
        """Raise error — no product selected yet."""
        # TODO: raise an appropriate error
        pass

    def cancel(self) -> int:
        """Refund all inserted money, transition to IdleState."""
        # TODO:
        # 1. Get current balance
        # 2. Reset balance to 0
        # 3. Transition to IdleState
        # 4. Return the refund amount
        pass


class DispensingState(VendingMachineState):
    """
    Product selected and paid for — ready to dispense.

    Valid actions: dispense
    Invalid actions: insert_money, select_product, cancel
    """

    def insert_money(self, amount: int) -> None:
        """Raise error — machine is dispensing."""
        # TODO: raise an appropriate error
        pass

    def select_product(self, slot: str) -> None:
        """Raise error — machine is dispensing."""
        # TODO: raise an appropriate error
        pass

    def dispense(self) -> int:
        """
        Dispense the product and return change.

        Steps:
        1. Get the selected product from inventory
        2. Deduct the price from balance
        3. Dispense one unit (reduce quantity)
        4. Calculate change (remaining balance)
        5. Reset balance to 0
        6. Clear selected slot
        7. Transition to IdleState
        8. Return the change
        """
        # TODO
        pass

    def cancel(self) -> int:
        """Raise error — already dispensing, too late to cancel."""
        # TODO: raise an appropriate error
        pass
