"""The same three retries, made safe with an Idempotency-Key.

The retry is correct: the client must ask again when it does not hear back.
The fix is for the client to put the same identifier on every attempt of
one charge, and for the server to remember which identifiers it has already
handled and skip the work the second time it sees one. The client picks the
key, because only the client knows the retries are one charge. Three
attempts now, one charge.

Run it with:  python3 idempotency_key.py
"""

import socket
import threading
import time

PORT = 8331
ledger = []
handled = set()          # every Idempotency-Key the server has already applied


def server():
    listening = socket.socket()
    listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listening.bind(("127.0.0.1", PORT))
    listening.listen(8)
    while True:
        connection, _ = listening.accept()
        request = connection.recv(4096).decode(errors="replace")
        key = ""
        for line in request.split("\r\n"):
            if line.lower().startswith("idempotency-key:"):
                key = line.split(":", 1)[1].strip()
        if key not in handled:
            handled.add(key)
            ledger.append(f"charge $30 ({key})")   # only the first time
        time.sleep(1.0)
        try:
            connection.sendall(b"HTTP/1.1 200 OK\r\n"
                               b"Content-Length: 3\r\n\r\nok\n")
        except OSError:
            pass
        connection.close()


threading.Thread(target=server, daemon=True).start()
time.sleep(0.3)

KEY = "charge-8f2c"       # one key for this charge, reused on every retry
for attempt in range(1, 4):
    client = socket.socket()
    client.settimeout(0.5)
    client.connect(("127.0.0.1", PORT))
    client.sendall(f"POST /charge HTTP/1.1\r\nHost: x\r\n"
                   f"Idempotency-Key: {KEY}\r\n\r\n".encode())
    try:
        client.recv(4096)
        print(f"attempt {attempt}: got a reply")
        break
    except socket.timeout:
        print(f"attempt {attempt}: no reply, retrying with the same key")
    client.close()

time.sleep(1.2)
print(f"\nthe card was charged {len(ledger)} time: {ledger}")
