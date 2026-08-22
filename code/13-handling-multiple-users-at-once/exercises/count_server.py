"""A threaded server with a shared counter and no lock.

Every request to /count reads a number, adds one, and writes it back,
the exact read-modify-write from race.py, now spread across threads that
the visitors create. Fire enough requests at once and the total comes out
short. Uncomment the two lock lines to fix it, and measure what the lock
costs the /slow page while you are there.

Run it with:  python3 count_server.py
Then, from another window:  python3 hammer.py
Stop it with control C.
"""

import socket
import threading
import time

hits = 0
lock = threading.Lock()


def response(body):
    head = (f"HTTP/1.1 200 OK\r\nContent-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n")
    return head.encode() + body


def handle(request):
    global hits
    target = request.split(b" ")[1] if request.count(b" ") >= 2 else b"/"
    if target == b"/count":
        # lock.acquire()          # <- uncomment these two lines for the fix
        current = hits             # read
        time.sleep(0)              # invite the scheduler to switch here
        hits = current + 1         # write
        # lock.release()
        return response(f"{hits}\n".encode())
    if target == b"/slow":
        time.sleep(0.5)
        return response(b"slow\n")
    return response(f"hits so far: {hits}\n".encode())


def serve(connection):
    connection.sendall(handle(connection.recv(65536)))
    connection.close()


server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8200))
server.listen(64)
print("listening on http://127.0.0.1:8200")
while True:
    connection, _ = server.accept()
    threading.Thread(target=serve, args=(connection,), daemon=True).start()
