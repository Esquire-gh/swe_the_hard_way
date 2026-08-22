"""A reverse proxy: one program in front of another.

It holds port 8000, the one the outside world connects to. For every
connection it opens a second socket to a backend on 8001, the application
server from chapter eleven, and then relays bytes in both directions until
both sides are done. The visitor thinks it is talking to one server. It is
talking to two, and the front one chose which.

Run a backend on 8001 first, for example:
    python3 -m http.server 8001
Then run this, and visit http://127.0.0.1:8000/.
Stop it with control C.
"""

import socket
import threading

FRONT = ("127.0.0.1", 8000)
BACK = ("127.0.0.1", 8001)


def relay(source, destination):
    """Copy bytes one way until the source has no more, then close."""
    try:
        while True:
            chunk = source.recv(65536)
            if not chunk:
                break
            destination.sendall(chunk)
    except OSError:
        pass
    finally:
        for sock in (source, destination):
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def handle(visitor):
    """Open a connection to the backend and pump both ways at once."""
    backend = socket.socket()
    try:
        backend.connect(BACK)
    except ConnectionRefusedError:
        visitor.sendall(b"HTTP/1.1 502 Bad Gateway\r\n"
                        b"Content-Length: 16\r\n\r\n502 bad gateway\n")
        visitor.close()
        return
    threading.Thread(target=relay, args=(visitor, backend), daemon=True).start()
    relay(backend, visitor)


server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(FRONT)
server.listen(16)
print(f"proxy on {FRONT[0]}:{FRONT[1]}, relaying to {BACK[0]}:{BACK[1]}")

while True:
    connection, _ = server.accept()
    threading.Thread(target=handle, args=(connection,), daemon=True).start()
