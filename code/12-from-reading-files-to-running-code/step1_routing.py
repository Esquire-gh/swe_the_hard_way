"""Serving pages that are produced by code rather than read off a disk.

Run it with:  python3 step1_routing.py
Then visit:   http://127.0.0.1:8000/ and http://127.0.0.1:8000/about
Stop it with control C.
"""

import socket


def response(status, body, kind="text/html"):
    """One HTTP response, headers and all, as bytes."""
    head = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {kind}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode() + body


def handle(request):
    """Work out which piece of code answers this request."""
    first_line = request.split(b"\r\n")[0].decode()
    method, target, _ = first_line.split(" ")

    if method != "GET":
        return response("405 Method Not Allowed", b"<h1>405 not allowed</h1>")
    if target == "/":
        return response("200 OK", b"<h1>Guestbook</h1><p>Nothing here yet.</p>")
    if target == "/about":
        return response("200 OK", b"<h1>About</h1><p>A guestbook.</p>")
    return response("404 Not Found", b"<h1>404 not found</h1>")


listening = socket.socket()
listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening.bind(("127.0.0.1", 8000))
listening.listen(5)
print("listening on http://127.0.0.1:8000")

while True:
    conversation, _ = listening.accept()
    conversation.sendall(handle(conversation.recv(65536)))
    conversation.close()
