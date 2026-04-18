# import socket
# import threading
#
#
# class FixEngine:
#     def __init__(self, host: str, port: int, sender_comp_id: str, target_comp_id: str):
#         self.host = host
#         self.port = port
#         self.sender_comp_id = sender_comp_id
#         self.target_comp_id = target_comp_id
#         self.seq_num = 1
#         self.sock = None
#         self.is_connected = False
#         self.message_callback = None
#
#     def connect(self):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.connect((self.host, self.port))
#         self.is_connected = True
#         threading.Thread(target=self._receive_loop, daemon=True).start()
#         self._send_logon()
#
#     def disconnect(self):
#         self._send_logout()
#         self.is_connected = False
#         if self.sock:
#             self.sock.close()
#
#     def set_message_callback(self, callback):
#         self.message_callback = callback
#
#     def send_message(self, msg_dict: dict):
#         msg_str = self._build_message(msg_dict)
#         if self.is_connected:
#             self.sock.sendall(msg_str.encode('ascii'))
#             self.seq_num += 1
#
#     def _receive_loop(self):
#         buffer = ""
#         while self.is_connected:
#             try:
#                 data = self.sock.recv(4096).decode('ascii')
#                 if not data:
#                     break
#                 buffer += data
#                 messages = buffer.split('\x0110=')
#                 for msg in messages[:-1]:
#                     full_msg = msg + '\x0110=000\x01'
#                     parsed_msg = self._parse_message(full_msg)
#                     if self.message_callback:
#                         self.message_callback(parsed_msg)
#                 buffer = messages[-1]
#             except Exception:
#                 break
#
#     def _build_message(self, msg_dict: dict) -> str:
#         body = []
#         for k, v in msg_dict.items():
#             if k not in ['MsgType']:
#                 body.append(f"{k}={v}")
#         body_str = "\x01".join(body) + "\x01" if body else ""
#
#         msg_type = msg_dict.get('MsgType', '0')
#         header = f"8=FIX.4.4\x019={len(body_str)}\x0135={msg_type}\x0134={self.seq_num}\x0149={self.sender_comp_id}\x0156={self.target_comp_id}\x01"
#
#         msg = header + body_str
#         checksum = sum(ord(c) for c in msg) % 256
#         msg += f"10={checksum:03d}\x01"
#         return msg
#
#     def _parse_message(self, msg_str: str) -> dict:
#         parsed = {}
#         pairs = msg_str.split('\x01')
#         for pair in pairs:
#             if '=' in pair:
#                 k, v = pair.split('=', 1)
#                 parsed[k] = v
#         return parsed
#
#     def _send_logon(self):
#         self.send_message({"MsgType": "A", "98": "0", "108": "30"})
#
#     def _send_logout(self):
#         self.send_message({"MsgType": "5"})


import socket
import threading
from datetime import datetime


class FixEngine:
    def __init__(self, host, port, sender_comp_id, target_comp_id):
        self.host = host
        self.port = port
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.seq_num = 1
        self.sock = None
        self.is_connected = False
        self.callback = None

    def set_message_callback(self, callback):
        self.callback = callback

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.is_connected = True
        threading.Thread(target=self._receive_loop, daemon=True).start()
        self._send_logon()

    def disconnect(self):
        self.is_connected = False
        if self.sock:
            self.sock.close()

    def send_order(self, cl_ord_id, symbol, side, qty, price):
        fix_side = "1" if side == "B" else "2"
        msg = (
            f"35=D\x01"
            f"11={cl_ord_id}\x01"
            f"55={symbol}\x01"
            f"54={fix_side}\x01"
            f"38={qty}\x01"
            f"44={price}\x01"
            f"40=2\x01"
            f"59=0\x01"
        )
        self._send_message(msg)

    def _send_logon(self):
        self._send_message("35=A\x0198=0\x01108=30\x01")

    def _send_message(self, body):
        time_str = datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
        header = (
            f"8=FIX.4.4\x01"
            f"34={self.seq_num}\x01"
            f"49={self.sender_comp_id}\x01"
            f"56={self.target_comp_id}\x01"
            f"52={time_str}\x01"
        )
        msg_data = header + body
        body_len = len(msg_data.replace("8=FIX.4.4\x01", ""))

        msg_with_len = f"8=FIX.4.4\x019={body_len}\x01" + msg_data[msg_data.find("34="):]

        checksum = sum(ord(c) for c in msg_with_len) % 256
        final_msg = f"{msg_with_len}10={checksum:03d}\x01"

        if self.is_connected:
            self.sock.sendall(final_msg.encode('ascii'))
            self.seq_num += 1

    def _receive_loop(self):
        buffer = ""
        while self.is_connected:
            try:
                data = self.sock.recv(4096).decode('ascii')
                if not data:
                    break
                buffer += data
                while "10=" in buffer:
                    end_idx = buffer.find("\x01", buffer.find("10=")) + 1
                    if end_idx == 0:
                        break
                    msg = buffer[:end_idx]
                    buffer = buffer[end_idx:]
                    self._parse_message(msg)
            except:
                break
        self.disconnect()

    def _parse_message(self, msg):
        if not self.callback:
            return

        parsed = {}
        for pair in msg.split("\x01"):
            if "=" in pair:
                tag, value = pair.split("=", 1)
                parsed[tag] = value
        self.callback(parsed)