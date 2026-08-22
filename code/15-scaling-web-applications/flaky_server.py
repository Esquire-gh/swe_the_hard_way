"""A server that answers a health check, or crashes on startup on command.

The supervisor next door restarts whatever it watches. This is the thing
it watches. Run normally it serves /health with "ok". Run with the word
"crash" it raises before it ever listens, so the supervisor can be shown
restarting a process that never actually works.

Run it with:      python3 flaky_server.py
Or, to crash:     python3 flaky_server.py crash
"""

import socket
import sys

if len(sys.argv) > 1 and sys.argv[1] == "crash":
    raise SystemExit("cannot start: pretend a config file is missing")

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8210))
server.listen(16)
print("healthy on http://127.0.0.1:8210", flush=True)
while True:
    connection, _ = server.accept()
    connection.recv(65536)
    body = b"ok\n"
    connection.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 3\r\n"
                        b"Connection: close\r\n\r\n" + body)
    connection.close()
