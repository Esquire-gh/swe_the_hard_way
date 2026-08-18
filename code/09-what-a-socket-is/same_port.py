"""Three connections to one port on one machine, told apart by the operating
system.

Run it with: python3 same_port.py
"""

import socket

TARGET = ("info.cern.ch", 80)

connections = []
for _ in range(3):
    connection = socket.socket()
    connection.connect(TARGET)
    connections.append(connection)

print("      this machine          the other machine")
for connection in connections:
    mine = connection.getsockname()
    theirs = connection.getpeername()
    print(f"fd {connection.fileno():<3} {mine[0]}:{mine[1]:<10}  {theirs[0]}:{theirs[1]}")

for connection in connections:
    connection.close()
