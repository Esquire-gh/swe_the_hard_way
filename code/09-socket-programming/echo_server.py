"""The first server in this course. It answers with whatever you send it.

Seven calls, in the order the operating system expects them: socket, bind,
listen, accept, recv, sendall, close. Everything in chapter ten is this
file with one of those lines doing more work.

Run it with:            python3 echo_server.py
Then in another window: python3 echo_client.py hello there
Stop it with control C.
"""

import socket

HOST, PORT = "127.0.0.1", 8000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"listening on {HOST}:{PORT}, descriptor {server_socket.fileno()}")

while True:
    # Nothing below this line runs until somebody connects.
    connection, address = server_socket.accept()
    number = connection.fileno()
    print(f"accepted {address[0]}:{address[1]} as descriptor {number}, "
          f"while the listening socket is still {server_socket.fileno()}")

    received = connection.recv(1024)
    connection.sendall(received)
    connection.close()
    print(f"    echoed {len(received)} bytes, closed descriptor {number}")
