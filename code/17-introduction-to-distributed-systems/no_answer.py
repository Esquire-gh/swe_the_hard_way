"""What a client learns when no answer comes back. Nothing at all.

Run it with: python3 no_answer.py
"""

import socket
import threading
import time

PORT = 8300
work_done = []


def server():
    """Slow, and completely healthy."""
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", PORT))
    server_socket.listen(5)
    while True:
        connection, _ = server_socket.accept()
        request = connection.recv(65536)
        time.sleep(1.5)                      # busy, not broken
        work_done.append(request.split(b" ")[1].decode())
        connection.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\nok\n")
        connection.close()


threading.Thread(target=server, daemon=True).start()
time.sleep(0.3)

client_socket = socket.socket()
client_socket.settimeout(0.5)
client_socket.connect(("127.0.0.1", PORT))
client_socket.sendall(b"GET /charge-the-card HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n")

believed = []
try:
    answer = client_socket.recv(65536)
    believed.append("/charge-the-card")
    print("the client got:", answer.split(b"\r\n")[0].decode())
except TimeoutError:
    print("the client gave up after half a second with no answer")
client_socket.close()

print(f"what the client can prove happened: {believed}")
time.sleep(1.5)
print(f"what actually happened:             {work_done}")
