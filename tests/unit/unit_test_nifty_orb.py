import pytest
from datetime import datetime, time
from src.strategies.active.nifty_orb_strategy import NiftyORBStrategy


class MockOMS:
    def __init__(self):
        self.orders = []

    def create_order(self, symbol, side, qty, price, type):
        order_id = "test_id"
        self.orders.append({"side": side, "price": price})
        return order_id


class MockRisk:
    def check_order(self, symbol, side, qty, price):
        return True


def test_orb_trigger_buy():
    oms = MockOMS()
    risk = MockRisk()
    strategy = NiftyORBStrategy(oms, risk)

    # Simulate range formation (9:15 - 9:30)
    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 16), 'price': 100})
    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 20), 'price': 110})
    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 25), 'price': 90})

    # High: 110, Low: 90

    # Tick after 9:30 breaking high
    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 31), 'price': 111})

    assert len(oms.orders) == 1
    assert oms.orders[0]['side'] == "B"
    assert oms.orders[0]['price'] == 111