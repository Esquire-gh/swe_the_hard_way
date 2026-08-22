"""An answer that arrives in pieces, which is why a chat window fills in a few
words at a time.

Run it with: python3 stream.py
"""

import socket
import threading
import time

PORT = 8400
ANSWER = "a model answering is a server writing text down a socket".split()


def server():
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", PORT))
    server_socket.listen(5)
    connection, _ = server_socket.accept()
    connection.recv(65536)

    connection.sendall(
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain\r\n"
        b"Transfer-Encoding: chunked\r\n\r\n"
    )
    for word in ANSWER:
        piece = (word + " ").encode()
        connection.sendall(f"{len(piece):x}\r\n".encode() + piece + b"\r\n")
        time.sleep(0.15)          # working out what comes next
    connection.sendall(b"0\r\n\r\n")
    connection.close()


threading.Thread(target=server, daemon=True).start()
time.sleep(0.3)

client_socket = socket.socket()
client_socket.connect(("127.0.0.1", PORT))
client_socket.sendall(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")

started = time.perf_counter()
while True:
    arrived = client_socket.recv(4096)
    if not arrived:
        break
    print(f"{time.perf_counter() - started:5.2f}s  {arrived!r}")
client_socket.close()
