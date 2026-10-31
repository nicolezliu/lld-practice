"""
Phased tests for the Vending Machine system.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models only
    python -m pytest tests.py -v -k "phase2"    # State transitions
    python -m pytest tests.py -v -k "phase3"    # VendingMachine integration

Each phase builds on the previous — start with phase1 and get all tests
green before moving on.
"""

import pytest

from models import Coin, Bill, Product, Inventory
from states import IdleState, HasMoneyState, DispensingState
from vending_machine import VendingMachine


# ===================================================================
# PHASE 1: Models — Enums, Product, Inventory
# ===================================================================

class TestPhase1Coins:
    """Verify coin enum values (in cents)."""

    def test_penny_value(self):
        assert Coin.PENNY.value == 1

    def test_nickel_value(self):
        assert Coin.NICKEL.value == 5

    def test_dime_value(self):
        assert Coin.DIME.value == 10

    def test_quarter_value(self):
        assert Coin.QUARTER.value == 25


class TestPhase1Bills:
    """Verify bill enum values (in cents)."""

    def test_one_dollar_value(self):
        assert Bill.ONE.value == 100

    def test_five_dollar_value(self):
        assert Bill.FIVE.value == 500


class TestPhase1Product:
    """Verify Product creation and behavior."""

    def test_product_creation(self):
        p = Product("Coca-Cola", price=150, quantity=5)
        assert p.name == "Coca-Cola"
        assert p.price == 150
        assert p.quantity == 5

    def test_product_is_available(self):
        p = Product("Water", price=100, quantity=3)
        assert p.is_available() is True

    def test_product_not_available_when_empty(self):
        p = Product("Water", price=100, quantity=0)
        assert p.is_available() is False

    def test_dispense_reduces_quantity(self):
        p = Product("Chips", price=125, quantity=2)
        p.dispense_one()
        assert p.quantity == 1

    def test_dispense_empty_raises(self):
        p = Product("Chips", price=125, quantity=0)
        with pytest.raises(ValueError):
            p.dispense_one()

    def test_restock_adds_quantity(self):
        p = Product("Chips", price=125, quantity=1)
        p.restock(5)
        assert p.quantity == 6


class TestPhase1Inventory:
    """Verify Inventory slot management."""

    def test_add_and_get_product(self):
        inv = Inventory()
        soda = Product("Soda", price=150, quantity=3)
        inv.add_product("A1", soda)
        assert inv.get_product("A1") is soda

    def test_add_duplicate_slot_raises(self):
        inv = Inventory()
        inv.add_product("A1", Product("Soda", price=150, quantity=3))
        with pytest.raises(ValueError):
            inv.add_product("A1", Product("Water", price=100, quantity=5))

    def test_get_missing_slot_raises(self):
        inv = Inventory()
        with pytest.raises(KeyError):
            inv.get_product("Z9")

    def test_has_slot(self):
        inv = Inventory()
        inv.add_product("B2", Product("Gum", price=75, quantity=10))
        assert inv.has_slot("B2") is True
        assert inv.has_slot("C3") is False

    def test_list_slots_sorted(self):
        inv = Inventory()
        inv.add_product("B1", Product("Water", price=100, quantity=5))
        inv.add_product("A1", Product("Soda", price=150, quantity=3))
        assert inv.list_slots() == ["A1", "B1"]


# ===================================================================
# PHASE 2: State Transitions
# ===================================================================

def _make_machine() -> VendingMachine:
    """Helper: create a loaded vending machine for state tests."""
    inv = Inventory()
    inv.add_product("A1", Product("Soda", price=150, quantity=5))
    inv.add_product("A2", Product("Water", price=100, quantity=3))
    inv.add_product("B1", Product("Chips", price=125, quantity=0))  # out of stock
    return VendingMachine(inv)


class TestPhase2IdleState:
    """Verify IdleState behavior."""

    def test_starts_in_idle(self):
        vm = _make_machine()
        assert isinstance(vm._state, IdleState)

    def test_insert_money_transitions_to_has_money(self):
        vm = _make_machine()
        vm.insert_money(Coin.QUARTER)
        assert isinstance(vm._state, HasMoneyState)

    def test_select_product_in_idle_raises(self):
        vm = _make_machine()
        with pytest.raises(Exception):
            vm.select_product("A1")

    def test_dispense_in_idle_raises(self):
        vm = _make_machine()
        with pytest.raises(Exception):
            vm.dispense()

    def test_cancel_in_idle_returns_zero(self):
        vm = _make_machine()
        refund = vm.cancel()
        assert refund == 0


class TestPhase2HasMoneyState:
    """Verify HasMoneyState behavior."""

    def test_insert_more_money_stays_in_has_money(self):
        vm = _make_machine()
        vm.insert_money(Coin.QUARTER)
        vm.insert_money(Coin.QUARTER)
        assert isinstance(vm._state, HasMoneyState)
        assert vm.get_balance() == 50

    def test_cancel_refunds_and_returns_to_idle(self):
        vm = _make_machine()
        vm.insert_money(Bill.ONE)
        refund = vm.cancel()
        assert refund == 100
        assert isinstance(vm._state, IdleState)
        assert vm.get_balance() == 0

    def test_select_product_transitions_to_dispensing(self):
        vm = _make_machine()
        vm.insert_money(Bill.ONE)
        vm.insert_money(Bill.ONE)  # 200 cents total
        vm.select_product("A1")    # Soda costs 150
        assert isinstance(vm._state, DispensingState)

    def test_select_insufficient_funds_raises(self):
        vm = _make_machine()
        vm.insert_money(Coin.QUARTER)  # 25 cents
        with pytest.raises(ValueError):
            vm.select_product("A1")   # Soda costs 150

    def test_select_out_of_stock_raises(self):
        vm = _make_machine()
        vm.insert_money(Bill.FIVE)    # plenty of money
        with pytest.raises(ValueError):
            vm.select_product("B1")   # Chips, quantity=0

    def test_select_invalid_slot_raises(self):
        vm = _make_machine()
        vm.insert_money(Bill.ONE)
        with pytest.raises((ValueError, KeyError)):
            vm.select_product("Z9")

    def test_dispense_without_selection_raises(self):
        vm = _make_machine()
        vm.insert_money(Bill.ONE)
        with pytest.raises(Exception):
            vm.dispense()


class TestPhase2DispensingState:
    """Verify DispensingState behavior."""

    def test_insert_money_while_dispensing_raises(self):
        vm = _make_machine()
        vm.insert_money(Bill.ONE)
        vm.insert_money(Bill.ONE)
        vm.select_product("A1")
        with pytest.raises(Exception):
            vm.insert_money(Coin.QUARTER)

    def test_cancel_while_dispensing_raises(self):
        vm = _make_machine()
        vm.insert_money(Bill.ONE)
        vm.insert_money(Bill.ONE)
        vm.select_product("A1")
        with pytest.raises(Exception):
            vm.cancel()


# ===================================================================
# PHASE 3: VendingMachine Integration
# ===================================================================

class TestPhase3BuyProduct:
    """Full buy flow: insert money → select → dispense."""

    def test_buy_exact_change(self):
        vm = _make_machine()
        # Soda costs 150: insert $1 + 2 quarters
        vm.insert_money(Bill.ONE)
        vm.insert_money(Coin.QUARTER)
        vm.insert_money(Coin.QUARTER)
        vm.select_product("A1")
        change = vm.dispense()
        assert change == 0
        assert vm.get_balance() == 0

    def test_buy_with_change(self):
        vm = _make_machine()
        # Soda costs 150: insert $2
        vm.insert_money(Bill.ONE)
        vm.insert_money(Bill.ONE)
        vm.select_product("A1")
        change = vm.dispense()
        assert change == 50  # 200 - 150
        assert vm.get_balance() == 0

    def test_buy_reduces_inventory(self):
        vm = _make_machine()
        product = vm.inventory.get_product("A1")
        original_qty = product.quantity
        vm.insert_money(Bill.ONE)
        vm.insert_money(Bill.ONE)
        vm.select_product("A1")
        vm.dispense()
        assert product.quantity == original_qty - 1

    def test_buy_then_back_to_idle(self):
        vm = _make_machine()
        vm.insert_money(Bill.ONE)
        vm.insert_money(Bill.ONE)
        vm.select_product("A1")
        vm.dispense()
        assert isinstance(vm._state, IdleState)

    def test_multiple_purchases(self):
        vm = _make_machine()
        # Buy soda twice
        for _ in range(2):
            vm.insert_money(Bill.ONE)
            vm.insert_money(Bill.ONE)
            vm.select_product("A1")
            vm.dispense()
        product = vm.inventory.get_product("A1")
        assert product.quantity == 3  # started with 5, bought 2

    def test_buy_cheapest_product(self):
        vm = _make_machine()
        # Water costs 100: insert $1
        vm.insert_money(Bill.ONE)
        vm.select_product("A2")
        change = vm.dispense()
        assert change == 0


class TestPhase3Cancel:
    """Cancel and refund flow."""

    def test_cancel_returns_full_amount(self):
        vm = _make_machine()
        vm.insert_money(Bill.FIVE)
        refund = vm.cancel()
        assert refund == 500
        assert isinstance(vm._state, IdleState)

    def test_cancel_with_mixed_money(self):
        vm = _make_machine()
        vm.insert_money(Bill.ONE)
        vm.insert_money(Coin.QUARTER)
        vm.insert_money(Coin.DIME)
        refund = vm.cancel()
        assert refund == 135  # 100 + 25 + 10

    def test_cancel_no_money_returns_zero(self):
        vm = _make_machine()
        refund = vm.cancel()
        assert refund == 0


class TestPhase3EdgeCases:
    """Edge cases and error scenarios."""

    def test_buy_last_item_then_out_of_stock(self):
        inv = Inventory()
        inv.add_product("A1", Product("LastOne", price=100, quantity=1))
        vm = VendingMachine(inv)
        # Buy the last one
        vm.insert_money(Bill.ONE)
        vm.select_product("A1")
        vm.dispense()
        # Try to buy again
        vm.insert_money(Bill.ONE)
        with pytest.raises(ValueError):
            vm.select_product("A1")

    def test_large_change(self):
        vm = _make_machine()
        # Water costs 100, insert $5
        vm.insert_money(Bill.FIVE)
        vm.select_product("A2")
        change = vm.dispense()
        assert change == 400  # 500 - 100

    def test_multiple_coins_accumulate(self):
        vm = _make_machine()
        # Insert 6 quarters = 150 cents (exact price of soda)
        for _ in range(6):
            vm.insert_money(Coin.QUARTER)
        assert vm.get_balance() == 150
        vm.select_product("A1")
        change = vm.dispense()
        assert change == 0
