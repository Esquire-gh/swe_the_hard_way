"""What listen(2) actually does when nobody is calling accept.

The queue you hand to listen is not a rescue. It holds a few connections
the operating system has completed on your behalf, and once it is full,
new visitors are turned away. This server never calls accept, so the queue
fills at once, and eight visitors knock. Watch which get in and which do
not.

Run it with:  python3 backlog.py
"""

import socket
import threading
import time

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8299))
server.listen(2)          # room for a couple, and the server never accepts

results = {}


def knock(number):
    client = socket.socket()
    client.settimeout(1.0)
    start = time.monotonic()
    try:
        client.connect(("127.0.0.1", 8299))
        waited = time.monotonic() - start
        results[number] = f"connected in {waited:.2f}s, now waiting"
    except socket.timeout:
        waited = time.monotonic() - start
        results[number] = f"gave up after {waited:.2f}s, queue full"
    except OSError as why:
        results[number] = f"refused: {why}"
    time.sleep(2.0)
    client.close()


visitors = [threading.Thread(target=knock, args=(n,)) for n in range(8)]
for visitor in visitors:
    visitor.start()
    time.sleep(0.02)
for visitor in visitors:
    visitor.join()

for number in range(8):
    print(f"visitor {number}: {results.get(number, '?')}")
server.close()
