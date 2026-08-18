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
    listening = socket.socket()
    listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listening.bind(("127.0.0.1", PORT))
    listening.listen(5)
    conversation, _ = listening.accept()
    conversation.recv(65536)

    conversation.sendall(
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain\r\n"
        b"Transfer-Encoding: chunked\r\n\r\n"
    )
    for word in ANSWER:
        piece = (word + " ").encode()
        conversation.sendall(f"{len(piece):x}\r\n".encode() + piece + b"\r\n")
        time.sleep(0.15)          # working out what comes next
    conversation.sendall(b"0\r\n\r\n")
    conversation.close()


threading.Thread(target=server, daemon=True).start()
time.sleep(0.3)

client = socket.socket()
client.connect(("127.0.0.1", PORT))
client.sendall(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")

started = time.perf_counter()
while True:
    arrived = client.recv(4096)
    if not arrived:
        break
    print(f"{time.perf_counter() - started:5.2f}s  {arrived!r}")
client.close()
