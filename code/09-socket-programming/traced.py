"""Both halves of the conversation in one process, so one strace shows all
of it. Nothing here is new: it is echo_server.py and echo_client.py with
the accept and the connect in the same file.

Run it under strace inside Linux with:
    strace -e trace=network python3 traced.py

Or on its own with: python3 traced.py
"""

import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", 8000))
server_socket.listen(5)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 8000))
connection, address = server_socket.accept()
client_socket.sendall(b"hello")
connection.recv(1024)
connection.sendall(b"hello")
client_socket.recv(1024)

connection.close()
client_socket.close()
server_socket.close()
print("done")
