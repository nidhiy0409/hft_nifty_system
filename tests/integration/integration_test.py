import pytest
from datetime import datetime
from src.strategies.active.nifty_orb_strategy import NiftyORBStrategy
from src.core.oms.order_management_system import OrderManagementSystem
from src.risk.pre_trade_checks.risk_manager import RiskManager


def test_strategy_oms_risk_integration():
    risk_manager = RiskManager(max_position_size=100)
    oms = OrderManagementSystem(ems_gateway=None)
    strategy = NiftyORBStrategy(oms, risk_manager)

    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 16), 'price': 10000})
    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 29), 'price': 10100})

    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 31), 'price': 10101})

    assert len(oms.active_orders) == 1
    order_id = list(oms.active_orders.keys())[0]
    assert oms.get_order_status(order_id) == "NEW"
    assert oms.active_orders[order_id]['price'] == 10101