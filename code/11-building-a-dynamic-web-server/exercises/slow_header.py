"""Exercise: hold a connection open by never finishing the request.

step4_session.py reads until it has the blank line that ends the headers.
This client sends half a header and then keeps the connection open without
sending the rest. The server sits in recv, holding the connection, unable
to accept anyone else, because chapter eight's blocking is doing exactly
what it was asked. Then the same server with one line added, a timeout,
which turns the wait into an error the server can answer.

Run it with:  python3 slow_header.py
"""

import socket
import threading
import time

TIMEOUT = 2.0


def serve(use_timeout):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 8066))
    server.listen(1)
    connection, _ = server.accept()
    if use_timeout:
        connection.settimeout(TIMEOUT)
    started = time.monotonic()
    data = b""
    try:
        while b"\r\n\r\n" not in data:
            chunk = connection.recv(65536)
            if not chunk:
                break
            data += chunk
        waited = time.monotonic() - started
        print(f"    request finished after {waited:.1f}s")
    except socket.timeout:
        waited = time.monotonic() - started
        print(f"    gave up after {waited:.1f}s and can answer 408 now")
    connection.close()
    server.close()


def half_a_header():
    time.sleep(0.3)
    client = socket.socket()
    client.connect(("127.0.0.1", 8066))
    client.sendall(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n")   # no blank line
    time.sleep(5.0)                                            # gone to lunch
    client.close()


for use_timeout in (False, True):
    label = "with a timeout" if use_timeout else "without a timeout"
    print(f"server {label}:")
    thread = threading.Thread(target=serve, args=(use_timeout,))
    thread.start()
    feeder = threading.Thread(target=half_a_header, daemon=True)
    feeder.start()
    thread.join(timeout=4.0)
    if thread.is_alive():
        print("    still waiting after 4s: this is the whole server, stuck")
        # We stop watching; the daemon feeder will close and free it.
        thread.join(timeout=6.0)
    print()
