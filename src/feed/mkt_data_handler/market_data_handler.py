import socket
import threading
import queue
import struct
import time


class MarketDataHandler:
    def __init__(self, feed_ip: str, feed_port: int, msg_queue: queue.Queue):
        self.feed_ip = feed_ip
        self.feed_port = feed_port
        self.msg_queue = msg_queue
        self.sock = None
        self.is_running = False
        self.listen_thread = None
        self.heartbeat_thread = None
        self.last_msg_time = time.time()

    def start_connection(self):
        self.is_running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.feed_ip, self.feed_port))

        self.listen_thread = threading.Thread(target=self._listen_for_data, daemon=True)
        self.heartbeat_thread = threading.Thread(target=self._monitor_heartbeat, daemon=True)

        self.listen_thread.start()
        self.heartbeat_thread.start()

    def stop_connection(self):
        self.is_running = False
        if self.sock:
            self.sock.close()

    def _listen_for_data(self):
        while self.is_running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                self.last_msg_time = time.time()
                self._process_raw_bytes(data)
            except Exception:
                break
        self.stop_connection()

    def _process_raw_bytes(self, data: bytes):
        decoded_msg = self._decode(data)
        if decoded_msg:
            self._publish(decoded_msg)

    def _decode(self, data: bytes) -> dict:
        try:
            msg_type, timestamp, symbol_id, price, qty = struct.unpack('!HQIdI', data[:26])
            return {
                "type": msg_type,
                "timestamp": timestamp,
                "symbol_id": symbol_id,
                "price": price,
                "qty": qty
            }
        except struct.error:
            return {}

    def _publish(self, message: dict):
        self.msg_queue.put(message)

    def _monitor_heartbeat(self):
        while self.is_running:
            time.sleep(1)
            if time.time() - self.last_msg_time > 5.0:
                self.stop_connection()
                try:
                    self.start_connection()
                except Exception:
                    pass