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
    listening = socket.socket()
    listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listening.bind(("127.0.0.1", PORT))
    listening.listen(5)
    while True:
        conversation, _ = listening.accept()
        request = conversation.recv(65536)
        time.sleep(1.5)                      # busy, not broken
        work_done.append(request.split(b" ")[1].decode())
        conversation.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\nok\n")
        conversation.close()


threading.Thread(target=server, daemon=True).start()
time.sleep(0.3)

client = socket.socket()
client.settimeout(0.5)
client.connect(("127.0.0.1", PORT))
client.sendall(b"GET /charge-the-card HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n")

believed = []
try:
    answer = client.recv(65536)
    believed.append("/charge-the-card")
    print("the client got:", answer.split(b"\r\n")[0].decode())
except TimeoutError:
    print("the client gave up after half a second with no answer")
client.close()

print(f"what the client can prove happened: {believed}")
time.sleep(1.5)
print(f"what actually happened:             {work_done}")
