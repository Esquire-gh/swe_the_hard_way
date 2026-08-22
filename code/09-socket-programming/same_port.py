"""Three connections to one port on one machine, told apart by the operating
system.

Run it with: python3 same_port.py
"""

import socket

TARGET = ("info.cern.ch", 80)

client_sockets = []
for _ in range(3):
    client_socket = socket.socket()
    client_socket.connect(TARGET)
    client_sockets.append(client_socket)

print("      this machine          the other machine")
for client_socket in client_sockets:
    mine = client_socket.getsockname()
    theirs = client_socket.getpeername()
    print(f"fd {client_socket.fileno():<3} {mine[0]}:{mine[1]:<10}  {theirs[0]}:{theirs[1]}")

for client_socket in client_sockets:
    client_socket.close()
