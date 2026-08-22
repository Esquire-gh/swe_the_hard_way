"""A client that retries three times, and a card charged three times.

Since a client that times out cannot tell whether the work was done, the
only move is to ask again. Here the server is slow but healthy: it charges
the card every time, then takes too long to reply, so the client gives up
and retries. Three attempts, three charges, and the customer is furious.

Run it with:  python3 retry_charges.py
"""

import socket
import threading
import time

PORT = 8330
ledger = []          # every charge the server actually made


def server():
    listening = socket.socket()
    listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listening.bind(("127.0.0.1", PORT))
    listening.listen(8)
    while True:
        connection, _ = listening.accept()
        connection.recv(4096)
        ledger.append("charge $30")      # the work happens at once
        time.sleep(1.0)                  # then the reply is too slow
        try:
            connection.sendall(b"HTTP/1.1 200 OK\r\n"
                                b"Content-Length: 3\r\n\r\nok\n")
        except OSError:
            pass
        connection.close()


threading.Thread(target=server, daemon=True).start()
time.sleep(0.3)

ATTEMPTS = 3
for attempt in range(1, ATTEMPTS + 1):
    client = socket.socket()
    client.settimeout(0.5)               # give up before the reply arrives
    client.connect(("127.0.0.1", PORT))
    client.sendall(b"POST /charge HTTP/1.1\r\nHost: x\r\n\r\n")
    try:
        client.recv(4096)
        print(f"attempt {attempt}: got a reply")
        break
    except socket.timeout:
        print(f"attempt {attempt}: no reply, retrying")
    client.close()

time.sleep(1.2)
print(f"\nthe card was charged {len(ledger)} times: {ledger}")
