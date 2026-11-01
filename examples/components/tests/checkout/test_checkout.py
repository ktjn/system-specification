"""Checkout tests: use a fake of the required reserve-inventory contract, never inventory internals."""
from src.checkout.app import place_order


def test_place_order():
    assert place_order("p1", 1, reserve=lambda p, q: True)["status"] == 201


def test_orders_api():
    assert place_order("p1", 9, reserve=lambda p, q: False) == {"status": 409, "error": "insufficient_inventory"}


def test_order_serialization():
    assert set(place_order("p1", 1, reserve=lambda p, q: True)["order"]) == {"product_id", "qty"}


def test_inventory_retry():
    assert place_order("p1", 1, reserve=lambda p, q: False)["status"] == 409  # illustrative: retry not implemented
