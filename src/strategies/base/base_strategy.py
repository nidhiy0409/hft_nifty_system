from abc import ABC, abstractmethod
from collections import deque
import statistics

class BaseStrategy(ABC):
    def __init__(self, oms, risk_manager):
        self.oms = oms
        self.risk_manager = risk_manager
        self.active_positions = {}
#
#     @abstractmethod
#     def on_tick(self, tick: dict):
#         """
#         Logic for processing individual price updates.
#         """
#         pass
#
#     @abstractmethod
#     def on_order_book_update(self, order_book):
#         """
#         Logic for processing Level 2 depth updates.
#         """
#         pass
#
#     @abstractmethod
#     def on_execution_report(self, report: dict):
#         """
#         Logic for handling order fills or rejections.
#         """
#         pass
#
#     def submit_buy_order(self, symbol: str, qty: int, price: float):
#         if self.risk_manager.check_order(symbol, "B", qty, price):
#             return self.oms.create_order(symbol, "B", qty, price, "LIMIT")
#         return None
#
#     def submit_sell_order(self, symbol: str, qty: int, price: float):
#         if self.risk_manager.check_order(symbol, "S", qty, price):
#             return self.oms.create_order(symbol, "S", qty, price, "LIMIT")
#         return None





class MeanReversionStrategy(BaseStrategy):
    def __init__(self, oms, risk_manager, window_size=100, z_score_threshold=2.0):
        super().__init__(oms, risk_manager)
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.prices = deque(maxlen=window_size)
        self.position = 0

    def on_tick(self, tick: dict):
        price = tick['price']
        self.prices.append(price)

        if len(self.prices) == self.window_size:
            mean = statistics.mean(self.prices)
            stdev = statistics.stdev(self.prices)

            if stdev == 0:
                return

            z_score = (price - mean) / stdev

            if z_score > self.z_score_threshold and self.position >= 0:
                self.submit_sell_order("NIFTY50", 50, price)
                self.position -= 50
            elif z_score < -self.z_score_threshold and self.position <= 0:
                self.submit_buy_order("NIFTY50", 50, price)
                self.position += 50
            elif abs(z_score) < 0.5 and self.position != 0:
                if self.position > 0:
                    self.submit_sell_order("NIFTY50", abs(self.position), price)
                else:
                    self.submit_buy_order("NIFTY50", abs(self.position), price)
                self.position = 0

    def on_order_book_update(self, order_book):
        pass

    def on_execution_report(self, report: dict):
        pass


class MarketMakerStrategy(BaseStrategy):
    def __init__(self, oms, risk_manager, spread_ticks=5, order_qty=100):
        super().__init__(oms, risk_manager)
        self.spread_ticks = spread_ticks
        self.order_qty = order_qty
        self.tick_size = 0.05
        self.current_bid_id = None
        self.current_ask_id = None

    def on_tick(self, tick: dict):
        pass

    def on_order_book_update(self, order_book):
        best_bid = order_book.get_best_bid()
        best_ask = order_book.get_best_ask()

        if best_bid > 0 and best_ask > 0:
            mid_price = (best_bid + best_ask) / 2

            my_bid_price = mid_price - (self.spread_ticks * self.tick_size)
            my_ask_price = mid_price + (self.spread_ticks * self.tick_size)

            if not self.current_bid_id:
                self.current_bid_id = self.submit_buy_order("NIFTY50", self.order_qty, my_bid_price)
            if not self.current_ask_id:
                self.current_ask_id = self.submit_sell_order("NIFTY50", self.order_qty, my_ask_price)

    def on_execution_report(self, report: dict):
        if report['status'] == 'FILLED':
            if report['order_id'] == self.current_bid_id:
                self.current_bid_id = None
            elif report['order_id'] == self.current_ask_id:
                self.current_ask_id = None