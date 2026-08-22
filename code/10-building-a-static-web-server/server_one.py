"""A web server. It answers everybody with the same page.

Run it with:  python3 server_one.py
Then visit:   http://127.0.0.1:8000
Stop it with control C.
"""

import socket

PAGE = b"""<!doctype html>
<html><body>
<h1>Hello from a socket</h1>
<p>This page was written by hand and sent down a file descriptor.</p>
</body></html>
"""

server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", 8000))
server_socket.listen(5)
print("listening on http://127.0.0.1:8000")

while True:
    connection, address = server_socket.accept()
    request = connection.recv(65536)

    print(f"--- {address[0]}:{address[1]} sent {len(request)} bytes ---")
    print(request.decode(errors="replace").rstrip())

    connection.sendall(
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html\r\n"
        b"Content-Length: " + str(len(PAGE)).encode() + b"\r\n"
        b"Connection: close\r\n"
        b"\r\n" + PAGE
    )
    connection.close()
