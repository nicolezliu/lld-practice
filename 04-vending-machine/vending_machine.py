"""
Core Vending Machine logic — the Context in the State pattern.

Your job: implement the VendingMachine class.
This is the public API that users interact with. It delegates behavior
to its current state object.

Think about:
- The machine owns the balance, inventory, and current state
- The state objects read/write machine state via the reference they hold
- How do you expose balance info to the user without breaking encapsulation?
"""

from typing import Optional, Union
from models import Coin, Bill, Product, Inventory
from states import VendingMachineState, IdleState


class VendingMachine:
    """
    The vending machine — context for the State pattern.

    The machine holds:
    - An Inventory of products in slots
    - A current balance (cents inserted by the user)
    - A selected_slot (set when user picks a product)
    - A state object that handles all actions
    """

    def __init__(self, inventory: Inventory):
        """
        Args:
            inventory: the loaded inventory of products
        """
        # TODO:
        # - Store inventory
        # - Initialize balance to 0
        # - Initialize selected_slot to None
        # - Set initial state to IdleState
        pass

    # ------------------------------------------------------------------
    # State management (called by state objects to transition)
    # ------------------------------------------------------------------

    def set_state(self, state: VendingMachineState) -> None:
        """Transition to a new state. Called by state objects."""
        # TODO
        pass

    # ------------------------------------------------------------------
    # Balance management (called by state objects)
    # ------------------------------------------------------------------

    def get_balance(self) -> int:
        """Return the current balance in cents."""
        # TODO
        pass

    def add_to_balance(self, amount: int) -> None:
        """Add cents to the balance."""
        # TODO
        pass

    def reset_balance(self) -> int:
        """Reset balance to 0 and return the old balance."""
        # TODO
        pass

    # ------------------------------------------------------------------
    # Slot selection (called by state objects)
    # ------------------------------------------------------------------

    def set_selected_slot(self, slot: Optional[str]) -> None:
        """Set or clear the currently selected slot."""
        # TODO
        pass

    def get_selected_slot(self) -> Optional[str]:
        """Return the currently selected slot code, or None."""
        # TODO
        pass

    # ------------------------------------------------------------------
    # Public API — delegated to the current state
    # ------------------------------------------------------------------

    def insert_money(self, money: Union[Coin, Bill]) -> None:
        """
        Insert a coin or bill.

        Delegates to the current state's insert_money method.
        """
        # TODO: delegate to self._state.insert_money(money.value)
        pass

    def select_product(self, slot: str) -> None:
        """
        Select a product by slot code.

        Delegates to the current state's select_product method.
        """
        # TODO: delegate to self._state.select_product(slot)
        pass

    def dispense(self) -> int:
        """
        Dispense the selected product.

        Returns:
            Change in cents.

        Delegates to the current state's dispense method.
        """
        # TODO: delegate to self._state.dispense()
        pass

    def cancel(self) -> int:
        """
        Cancel the current transaction.

        Returns:
            Refund amount in cents.

        Delegates to the current state's cancel method.
        """
        # TODO: delegate to self._state.cancel()
        pass

    @property
    def inventory(self) -> Inventory:
        """Return the inventory (for state objects to access)."""
        # TODO
        pass

    def display(self) -> None:
        """Print a human-readable status of the machine."""
        # TODO: show balance, state, available products
        pass
