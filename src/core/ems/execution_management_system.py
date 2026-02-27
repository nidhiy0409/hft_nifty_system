class ExecutionManagementSystem:
    def __init__(self, fix_engine, oms):
        self.fix_engine = fix_engine
        self.oms = oms

    def send_order(self, order: dict):
        fix_msg = self._translate_to_fix(order)
        self.fix_engine.send_message(fix_msg)

    def send_cancel(self, order_id: str):
        cancel_msg = self._create_cancel_request(order_id)
        self.fix_engine.send_message(cancel_msg)

    def on_message_received(self, message: dict):
        if message.get("MsgType") == "8":
            execution_report = self._parse_execution_report(message)
            self.oms.process_execution_report(execution_report)

    def _translate_to_fix(self, order: dict) -> dict:
        return {
            "MsgType": "D",
            "ClOrdID": order.get("order_id"),
            "Symbol": order.get("symbol"),
            "Side": "1" if order.get("side") == "B" else "2",
            "OrderQty": order.get("qty"),
            "Price": order.get("price"),
            "OrdType": "2" if order.get("order_type") == "LIMIT" else "1"
        }

    def _create_cancel_request(self, order_id: str) -> dict:
        return {
            "MsgType": "F",
            "OrigClOrdID": order_id,
            "ClOrdID": f"{order_id}_C"
        }

    def _parse_execution_report(self, message: dict) -> dict:
        exec_type_map = {
            "0": "NEW",
            "1": "PARTIAL_FILL",
            "2": "FILL",
            "4": "CANCELED",
            "8": "REJECTED"
        }
        return {
            "order_id": message.get("ClOrdID"),
            "exec_type": exec_type_map.get(message.get("ExecType"), "UNKNOWN"),
            "last_qty": float(message.get("LastQty", 0)),
            "last_px": float(message.get("LastPx", 0)),
            "leaves_qty": float(message.get("LeavesQty", 0))
        }