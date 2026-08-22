"""Send one request in two pieces, the way a network is allowed to.

Nothing here is unusual. The bytes are correct and they arrive in order.
They are just not all there at the moment the server calls recv once.

Start server_files.py or server_safe.py first.
Run it with: python3 split_request.py
"""

import socket
import time

FIRST = b"GET /ab"
REST = b"out.html HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"

client_socket = socket.socket()
try:
    client_socket.connect(("127.0.0.1", 8000))
except ConnectionRefusedError:
    raise SystemExit("nothing on 8000: start server_files.py first")

client_socket.sendall(FIRST)
print(f"sent {FIRST!r}, which is {len(FIRST)} bytes of a "
      f"{len(FIRST) + len(REST)} byte request, then paused")
time.sleep(0.3)

client_socket.settimeout(1.0)
answer = b""
try:
    while True:
        piece = client_socket.recv(4096)
        if not piece:
            break
        answer += piece
except (socket.timeout, ConnectionResetError):
    pass

if not answer:
    print("no answer yet: the server is still waiting for the rest")
else:
    head, _, body = answer.partition(b"\r\n\r\n")
    print("\nthe server answered before the request finished arriving")
    print(f"    status      {head.splitlines()[0].decode()}")
    for line in body.decode(errors="replace").splitlines():
        if "<h1>" in line:
            print(f"    page sent   {line.strip()}")
            break
    print("    page asked for   /about.html")

try:
    client_socket.sendall(REST)
    print(f"\nsent the other {len(REST)} bytes, which nobody will read")
except OSError as gone:
    print(f"\nsending the rest failed: {type(gone).__name__}, server hung up")
client_socket.close()
