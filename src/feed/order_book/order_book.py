import collections


class OrderBook:
    def __init__(self, symbol_id: int):
        self.symbol_id = symbol_id
        self.bids = collections.defaultdict(int)
        self.asks = collections.defaultdict(int)
        self.orders = {}

    def add_order(self, order_id: int, side: str, price: float, qty: int):
        self.orders[order_id] = {'side': side, 'price': price, 'qty': qty}
        if side == 'B':
            self.bids[price] += qty
        else:
            self.asks[price] += qty

    def modify_order(self, order_id: int, new_qty: int):
        if order_id in self.orders:
            order = self.orders[order_id]
            old_qty = order['qty']
            side = order['side']
            price = order['price']

            delta = new_qty - old_qty
            order['qty'] = new_qty

            if side == 'B':
                self.bids[price] += delta
            else:
                self.asks[price] += delta

    def cancel_order(self, order_id: int):
        if order_id in self.orders:
            order = self.orders.pop(order_id)
            side = order['side']
            price = order['price']
            qty = order['qty']

            if side == 'B':
                self.bids[price] -= qty
                if self.bids[price] <= 0:
                    del self.bids[price]
            else:
                self.asks[price] -= qty
                if self.asks[price] <= 0:
                    del self.asks[price]

    def get_best_bid(self) -> float:
        return max(self.bids.keys(), default=0.0)

    def get_best_ask(self) -> float:
        return min(self.asks.keys(), default=0.0)