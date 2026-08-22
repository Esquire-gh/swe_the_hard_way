"""The other end of echo_server.py: two calls to get connected, then read
and write like anything else.

Run it with: python3 echo_client.py hello there
"""

import socket
import sys

HOST, PORT = "127.0.0.1", 8000
message = " ".join(sys.argv[1:]) or "hello"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

mine = client_socket.getsockname()
theirs = client_socket.getpeername()
print(f"descriptor {client_socket.fileno()}: "
      f"{mine[0]}:{mine[1]} -> {theirs[0]}:{theirs[1]}")

client_socket.sendall(message.encode())
print(f"sent    {message!r}")
print(f"got back {client_socket.recv(1024)!r}")
client_socket.close()
