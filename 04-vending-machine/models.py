"""
Models for the Vending Machine system.

Your job: fill in the class bodies.
- Think about how money is represented (cents avoid floating-point issues)
- Think about how products map to slot codes (like "A1", "B2")
- Think about what operations the Inventory needs to support
"""

from enum import Enum


# ---------------------------------------------------------------------------
# Enums — money types
# ---------------------------------------------------------------------------

class Coin(Enum):
    """
    Coins the machine accepts. Value is in cents.

    Think about: why cents instead of dollars?
    (Hint: floating-point arithmetic is tricky with money.)
    """
    # TODO: define members — PENNY, NICKEL, DIME, QUARTER
    pass


class Bill(Enum):
    """
    Bills the machine accepts. Value is in cents.
    """
    # TODO: define members — ONE (100 cents), FIVE (500 cents)
    pass


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

class Product:
    """
    A product available in the vending machine.

    Think about:
    - What identifies a product? (name)
    - What's its price? (in cents to avoid float issues)
    - How do you track quantity?
    """

    def __init__(self, name: str, price: int, quantity: int = 0):
        """
        Args:
            name: display name (e.g. "Coca-Cola")
            price: price in cents (e.g. 150 = $1.50)
            quantity: number of items in stock
        """
        # TODO: store name, price, validate price > 0, store quantity
        pass

    def is_available(self) -> bool:
        """Return True if at least one unit is in stock."""
        # TODO
        pass

    def dispense_one(self) -> None:
        """
        Reduce quantity by one.
        Raise ValueError if already out of stock.
        """
        # TODO
        pass

    def restock(self, amount: int) -> None:
        """Add `amount` units to inventory."""
        # TODO
        pass

    def __repr__(self) -> str:
        # TODO: useful debug representation
        return f"Product({self.name})"


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

class Inventory:
    """
    Manages products by slot code (e.g. "A1", "A2", "B1").

    Think about:
    - How do you map slot codes to products?
    - What happens if someone requests a slot that doesn't exist?
    - Should adding a product to an occupied slot overwrite or raise?
    """

    def __init__(self):
        # TODO: initialize the slot → product mapping
        pass

    def add_product(self, slot: str, product: Product) -> None:
        """
        Add a product to the given slot.
        Raise ValueError if the slot is already occupied.
        """
        # TODO
        pass

    def get_product(self, slot: str) -> Product:
        """
        Return the product in the given slot.
        Raise KeyError if the slot doesn't exist.
        """
        # TODO
        pass

    def has_slot(self, slot: str) -> bool:
        """Return True if the slot code exists in the inventory."""
        # TODO
        pass

    def list_slots(self) -> list[str]:
        """Return a sorted list of all slot codes."""
        # TODO
        pass

    def __repr__(self) -> str:
        # TODO
        return "Inventory(...)"
