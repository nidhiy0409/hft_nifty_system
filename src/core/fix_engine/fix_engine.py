import socket
import threading


class FixEngine:
    def __init__(self, host: str, port: int, sender_comp_id: str, target_comp_id: str):
        self.host = host
        self.port = port
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.seq_num = 1
        self.sock = None
        self.is_connected = False
        self.message_callback = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.is_connected = True
        threading.Thread(target=self._receive_loop, daemon=True).start()
        self._send_logon()

    def disconnect(self):
        self._send_logout()
        self.is_connected = False
        if self.sock:
            self.sock.close()

    def set_message_callback(self, callback):
        self.message_callback = callback

    def send_message(self, msg_dict: dict):
        msg_str = self._build_message(msg_dict)
        if self.is_connected:
            self.sock.sendall(msg_str.encode('ascii'))
            self.seq_num += 1

    def _receive_loop(self):
        buffer = ""
        while self.is_connected:
            try:
                data = self.sock.recv(4096).decode('ascii')
                if not data:
                    break
                buffer += data
                messages = buffer.split('\x0110=')
                for msg in messages[:-1]:
                    full_msg = msg + '\x0110=000\x01'
                    parsed_msg = self._parse_message(full_msg)
                    if self.message_callback:
                        self.message_callback(parsed_msg)
                buffer = messages[-1]
            except Exception:
                break

    def _build_message(self, msg_dict: dict) -> str:
        body = []
        for k, v in msg_dict.items():
            if k not in ['MsgType']:
                body.append(f"{k}={v}")
        body_str = "\x01".join(body) + "\x01" if body else ""

        msg_type = msg_dict.get('MsgType', '0')
        header = f"8=FIX.4.4\x019={len(body_str)}\x0135={msg_type}\x0134={self.seq_num}\x0149={self.sender_comp_id}\x0156={self.target_comp_id}\x01"

        msg = header + body_str
        checksum = sum(ord(c) for c in msg) % 256
        msg += f"10={checksum:03d}\x01"
        return msg

    def _parse_message(self, msg_str: str) -> dict:
        parsed = {}
        pairs = msg_str.split('\x01')
        for pair in pairs:
            if '=' in pair:
                k, v = pair.split('=', 1)
                parsed[k] = v
        return parsed

    def _send_logon(self):
        self.send_message({"MsgType": "A", "98": "0", "108": "30"})

    def _send_logout(self):
        self.send_message({"MsgType": "5"})