import socket
import threading


class MockExchange:
    def __init__(self, host='127.0.0.1', port=5001):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.is_running = False

    def start(self):
        self.is_running = True
        self.server.listen(1)
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        while self.is_running:
            conn, addr = self.server.accept()
            threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()

    def _handle_client(self, conn):
        while self.is_running:
            try:
                data = conn.recv(4096).decode('ascii')
                if not data: break

                if "35=D" in data:
                    cl_ord_id = self._extract_tag(data, "11")
                    symbol = self._extract_tag(data, "55")
                    qty = self._extract_tag(data, "38")
                    price = self._extract_tag(data, "44")

                    report = f"8=FIX.4.4\x019=0\x0135=8\x0134=1\x0149=EXCH\x0156=TRADER\x0111={cl_ord_id}\x0117={cl_ord_id}_exec\x01150=2\x0139=2\x0155={symbol}\x0138={qty}\x0144={price}\x0132={qty}\x0131={price}\x01151=0\x0110=000\x01"
                    conn.sendall(report.encode('ascii'))
            except:
                break
        conn.close()

    def _extract_tag(self, msg, tag):
        parts = msg.split('\x01')
        for p in parts:
            if p.startswith(f"{tag}="):
                return p.split('=')[1]
        return ""

    def stop(self):
        self.is_running = False
        self.server.close()