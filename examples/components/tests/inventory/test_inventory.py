from src.inventory.api import reserve


def test_reserve_never_goes_negative():
    assert reserve("p1", 99) is False
