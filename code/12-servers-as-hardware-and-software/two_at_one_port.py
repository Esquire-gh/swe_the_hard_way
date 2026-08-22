"""One machine can hold many servers. One port can hold one.

Run it with: python3 two_at_one_port.py
"""

import socket


def claim(port):
    """Try to become the program that answers on this port."""
    server_socket = socket.socket()
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(5)
    return listening


first = claim(8200)
print("claimed port 8200")

second = claim(8201)
print("claimed port 8201 as well, on the same machine")

try:
    claim(8200)
except OSError as refused:
    print(f"asking for port 8200 again: {refused.strerror}")

first.close()
second.close()
