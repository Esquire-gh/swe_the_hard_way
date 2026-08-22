"""A threaded server whose page does real per-request work, like a real one.

The trivial pages in chapter thirteen answer in microseconds, which hides
the ceiling. A real page reads a database and renders HTML, a few
milliseconds of actual work. This does about five milliseconds of it per
request, in a thread per visitor, so load.py can find the rate at which
this machine falls over, which is the number the cache section starts from.

Run it with:  python3 work_server.py
Then, from another window:  python3 load.py   (point it at /work)
Stop it with control C.
"""

import socket
import threading


def build_page():
    """About five milliseconds of CPU, standing in for a real page."""
    total = 0
    for n in range(250_000):
        total += n * n
    return f"<p>{total}</p>".encode()


def response(body):
    head = (f"HTTP/1.1 200 OK\r\nContent-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n")
    return head.encode() + body


def serve(connection):
    connection.recv(65536)
    connection.sendall(response(build_page()))
    connection.close()


server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8200))
server.listen(64)
print("listening on http://127.0.0.1:8200, a page that does real work")
while True:
    connection, _ = server.accept()
    threading.Thread(target=serve, args=(connection,), daemon=True).start()
