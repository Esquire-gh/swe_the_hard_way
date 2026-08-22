"""Exercise two: a connection that lasts longer than one message.

echo_server.py reads once and hangs up. A real conversation is a loop on
one descriptor: read, answer, read again, until the other end closes and
recv returns nothing at all. That empty result is the only way you find
out they have gone.

Run it with:            python3 echo_conversation.py
Then in another window: python3 talk.py
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
    connection, address = server_socket.accept()
    mine = connection.getsockname()
    theirs = connection.getpeername()
    print(f"descriptor {connection.fileno()}: "
          f"{theirs[0]}:{theirs[1]} -> {mine[0]}:{mine[1]}")

    said = 0
    while True:
        received = connection.recv(1024)
        if not received:                 # the other end closed its side
            break
        said += 1
        connection.sendall(received.upper())
        print(f"    {said}: {received!r}")

    connection.close()
    print(f"    they said {said} things and went away")
