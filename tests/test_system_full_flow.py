import pytest
import time
from datetime import datetime
from tests.mock_exchange import MockExchange
from src.core.fix_engine.fix_engine import FixEngine
from src.core.oms.order_management_system import OrderManagementSystem
from src.core.ems.execution_management_system import ExecutionManagementSystem
from src.risk.pre_trade_checks.risk_manager import RiskManager
from src.strategies.active.nifty_orb_strategy import NiftyORBStrategy


def test_full_system_execution_flow():
    exchange = MockExchange(port=5002)
    exchange.start()
    time.sleep(1)

    fix_engine = FixEngine("127.0.0.1", 5002, "TRADER", "EXCH")
    oms = OrderManagementSystem(ems_gateway=None)
    ems = ExecutionManagementSystem(fix_engine, oms)
    oms.ems_gateway = ems
    fix_engine.set_message_callback(ems.on_message_received)

    risk_manager = RiskManager(max_position_size=1000)
    strategy = NiftyORBStrategy(oms, risk_manager)

    fix_engine.connect()
    time.sleep(1)

    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 16), 'price': 22000})
    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 29), 'price': 22100})
    strategy.on_tick({'timestamp': datetime(2026, 4, 18, 9, 31), 'price': 22105})

    timeout = time.time() + 5
    while time.time() < timeout:
        order_id = list(oms.active_orders.keys())[0] if oms.active_orders else None
        if order_id and oms.get_order_status(order_id) == "FILLED":
            break
        time.sleep(0.1)

    order_id = list(oms.active_orders.keys())[0]
    assert oms.get_order_status(order_id) == "FILLED"
    assert oms.active_orders[order_id]['filled_qty'] == 50

    fix_engine.disconnect()
    exchange.stop()