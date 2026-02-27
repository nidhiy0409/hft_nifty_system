import uuid
from typing import Dict, Any


class OrderManagementSystem:
    def __init__(self, ems_gateway):
        self.ems_gateway = ems_gateway
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        self.execution_history = []

    def create_order(self, symbol: str, side: str, qty: int, price: float, order_type: str) -> str:
        order_id = str(uuid.uuid4())
        order_details = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": price,
            "order_type": order_type,
            "status": "NEW",
            "filled_qty": 0
        }
        self.active_orders[order_id] = order_details
        return order_id

    def submit_order(self, order_id: str):
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            order["status"] = "PENDING_SUBMIT"
            self.ems_gateway.send_order(order)

    def cancel_order(self, order_id: str):
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            order["status"] = "PENDING_CANCEL"
            self.ems_gateway.send_cancel(order_id)

    def process_execution_report(self, report: Dict[str, Any]):
        order_id = report.get("order_id")
        if order_id in self.active_orders:
            order = self.active_orders[order_id]
            exec_type = report.get("exec_type")

            if exec_type == "REJECTED":
                order["status"] = "REJECTED"
            elif exec_type == "CANCELED":
                order["status"] = "CANCELED"
            elif exec_type == "PARTIAL_FILL" or exec_type == "FILL":
                filled_qty = report.get("last_qty", 0)
                order["filled_qty"] += filled_qty

                if order["filled_qty"] >= order["qty"]:
                    order["status"] = "FILLED"
                else:
                    order["status"] = "PARTIALLY_FILLED"

                self.execution_history.append(report)

    def get_order_status(self, order_id: str) -> str:
        if order_id in self.active_orders:
            return self.active_orders[order_id]["status"]
        return "UNKNOWN"