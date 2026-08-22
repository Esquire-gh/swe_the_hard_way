"""A deploy with no dropped request, using chapter twelve's reverse proxy.

To install a new version you stop the old process and start the new one,
and between those two moments there is no server. The way out is to start
the new version first, on a second port, point the proxy at it, and only
then stop the old one. This runs two backends and a proxy, sends a steady
stream of requests throughout, switches the proxy from version one to
version two mid-stream, and counts how many requests failed.

Run it with:  python3 deploy.py
"""

import http.client
import socket
import threading
import time

FRONT = ("127.0.0.1", 8300)
V1 = ("127.0.0.1", 8301)
V2 = ("127.0.0.1", 8302)

backend = {"where": V1}          # the proxy reads this; the deploy rewrites it
requests_made = 0
failures = 0
stop = threading.Event()
callers_stop = threading.Event()


def version_server(address, name):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(address)
    server.listen(16)
    server.settimeout(0.5)
    body = f"served by {name}\n".encode()
    reply = (b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n"
             b"Connection: close\r\n\r\n" % len(body)) + body
    while not stop.is_set():
        try:
            connection, _ = server.accept()
        except socket.timeout:
            continue
        connection.recv(65536)
        connection.sendall(reply)
        connection.close()
    server.close()


def proxy():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(FRONT)
    server.listen(64)
    server.settimeout(0.5)
    while not stop.is_set():
        try:
            visitor, _ = server.accept()
        except socket.timeout:
            continue
        upstream = socket.socket()
        upstream.connect(backend["where"])      # whichever version is current
        upstream.sendall(visitor.recv(65536))
        visitor.sendall(upstream.recv(65536))
        upstream.close()
        visitor.close()
    server.close()


def caller():
    global requests_made, failures
    while not callers_stop.is_set():
        try:
            conn = http.client.HTTPConnection(*FRONT, timeout=2)
            conn.request("GET", "/")
            conn.getresponse().read()
            conn.close()
            requests_made += 1
        except OSError:
            failures += 1
        time.sleep(0.002)


threads = [
    threading.Thread(target=version_server, args=(V1, "version 1"),
                     daemon=True),
    threading.Thread(target=version_server, args=(V2, "version 2"),
                     daemon=True),
    threading.Thread(target=proxy, daemon=True),
]
for thread in threads:
    thread.start()
time.sleep(0.3)

callers = [threading.Thread(target=caller, daemon=True) for _ in range(5)]
for thread in callers:
    thread.start()

time.sleep(0.5)
print("version 2 is up on its own port; switching the proxy over now")
backend["where"] = V2                    # the entire deploy, one assignment
time.sleep(0.5)

callers_stop.set()                       # stop calling, let in-flight finish
time.sleep(0.3)
stop.set()                               # only now take the servers down
time.sleep(0.6)
print(f"requests served through the switch: {requests_made}")
print(f"requests that failed:               {failures}")
