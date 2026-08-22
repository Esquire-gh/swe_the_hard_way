"""The same server, with each connection handled in a thread of its own.

Run it with:  python3 one_at_a_time_threaded.py
Stop it with control C.
"""

import socket
import threading
import time


def response(body):
    head = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode() + body


def handle(request):
    target = request.split(b" ")[1] if request.count(b" ") >= 2 else b"/"
    if target == b"/slow":
        time.sleep(2)          # stands in for a large file or a slow database
        return response(b"slow page\n")
    return response(b"fast page\n")


server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", 8200))
server_socket.listen(5)
print("listening on http://127.0.0.1:8200")


# BEGIN threads
def serve(connection):
    """Everything that used to happen inside the loop."""
    connection.sendall(handle(connection.recv(65536)))
    connection.close()


while True:
    connection, _ = server_socket.accept()
    threading.Thread(target=serve, args=(connection,), daemon=True).start()
# END threads
