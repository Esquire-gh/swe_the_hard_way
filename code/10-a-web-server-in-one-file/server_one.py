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

listening = socket.socket()
listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening.bind(("127.0.0.1", 8000))
listening.listen(5)
print("listening on http://127.0.0.1:8000")

while True:
    conversation, who = listening.accept()
    request = conversation.recv(65536)

    print(f"--- {who[0]}:{who[1]} sent {len(request)} bytes ---")
    print(request.decode(errors="replace").rstrip())

    conversation.sendall(
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html\r\n"
        b"Content-Length: " + str(len(PAGE)).encode() + b"\r\n"
        b"Connection: close\r\n"
        b"\r\n" + PAGE
    )
    conversation.close()
