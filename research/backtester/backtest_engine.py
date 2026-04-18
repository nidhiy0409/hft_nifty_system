# from typing import Any, Dict
#
# class BacktestEngine:
#     def __init__(self, strategy: Any, tick_processor: Any):
#         self.strategy = strategy
#         self.tick_processor = tick_processor
#         self.positions = {}
#         self.trades = []
#         self.pnl = 0.0
#
#     def run(self):
#         self.tick_processor.load_data()
#         for tick in self.tick_processor.stream_ticks():
#             self.strategy.on_tick(tick)
#             self._check_simulated_executions()
#
#     def _check_simulated_executions(self):
#         pass
#
#     def get_results(self) -> Dict[str, Any]:
#         return {
#             "total_trades": len(self.trades),
#             "pnl": self.pnl,
#             "positions": self.positions
#         }

import pandas as pd
from typing import Type
from src.core.oms.order_management_system import OrderManagementSystem
from src.core.matching_engine.simulated_matching_engine import SimulatedMatchingEngine
from src.risk.pre_trade_checks.risk_manager import RiskManager
from src.strategies.base.base_strategy import BaseStrategy


class BacktestExecutionGateway:
    def __init__(self, matching_engine: SimulatedMatchingEngine, oms: OrderManagementSystem):
        self.matching_engine = matching_engine
        self.oms = oms
        self.processed_trades_count = 0

    def send_order(self, order: dict):
        self.matching_engine.process_order(order)

    def poll_executions(self):
        while self.processed_trades_count < len(self.matching_engine.trades):
            trade = self.matching_engine.trades[self.processed_trades_count]
            self.processed_trades_count += 1

            if trade['buyer_id'] in self.oms.active_orders:
                self.oms.update_order(trade['buyer_id'], "FILLED", trade['price'], trade['qty'])

            if trade['seller_id'] in self.oms.active_orders:
                self.oms.update_order(trade['seller_id'], "FILLED", trade['price'], trade['qty'])


class BacktestEngine:
    def __init__(self, tick_processor, strategy_class: Type[BaseStrategy]):
        self.tick_processor = tick_processor
        self.matching_engine = SimulatedMatchingEngine()
        self.oms = OrderManagementSystem(ems_gateway=None)
        self.gateway = BacktestExecutionGateway(self.matching_engine, self.oms)
        self.oms.ems_gateway = self.gateway
        self.risk_manager = RiskManager(max_position_size=1000, max_daily_loss=-100000)
        self.strategy = strategy_class(self.oms, self.risk_manager)

    def run(self):
        self.tick_processor.load_data()

        for tick in self.tick_processor.stream_ticks():
            self.strategy.on_tick(tick)

            for order_id, order_data in list(self.oms.active_orders.items()):
                if order_data['status'] == 'NEW':
                    me_order = {
                        'order_id': order_id,
                        'side': order_data['side'],
                        'qty': order_data['qty'],
                        'price': order_data['price'],
                        'type': order_data['type']
                    }
                    self.gateway.send_order(me_order)
                    self.oms.update_order(order_id, "PENDING", order_data['price'], 0)

            self.gateway.poll_executions()

        return self.matching_engine.trades