"""The client for echo_conversation.py: several messages, one connection.

Run it with: python3 talk.py
"""

import socket

HOST, PORT = "127.0.0.1", 8000
LINES = ["one", "two", "three"]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
mine = client_socket.getsockname()
print(f"descriptor {client_socket.fileno()}, my end is port {mine[1]}")

for line in LINES:
    client_socket.sendall(line.encode())
    print(f"    sent {line!r}, got back {client_socket.recv(1024)!r}")

client_socket.close()
print("closed. the server's recv will now return b'' and it will notice.")
