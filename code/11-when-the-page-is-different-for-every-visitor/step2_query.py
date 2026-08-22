"""Reading what the visitor typed into the address, and what happens to a page
when you put it back without care.

The /hello page here puts the visitor's text into the page unchanged, which is
the bug chapter 12 is about. /hello-escaped is the same page done properly. Do
not copy the first one anywhere.

Run it with:  python3 step2_query.py
Then visit:   http://127.0.0.1:8000/hello?name=Ada
Stop it with control C.
"""

import socket
from urllib.parse import unquote_plus


def response(status, body, kind="text/html"):
    head = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {kind}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode() + body


def split_target(target):
    """Separate the path from the fields written after the question mark."""
    path, _, query = target.partition("?")
    fields = {}
    for pair in query.split("&"):
        if not pair:
            continue
        name, _, value = pair.partition("=")
        fields[unquote_plus(name)] = unquote_plus(value)
    return path, fields


def escape(text):
    """Make text safe to place inside a page."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def handle(request):
    first_line = request.split(b"\r\n")[0].decode()
    method, target, _ = first_line.split(" ")
    path, fields = split_target(target)

    if method != "GET":
        return response("405 Method Not Allowed", b"<h1>405 not allowed</h1>")
    if path == "/hello":
        name = fields.get("name", "stranger")
        return response("200 OK", f"<h1>Hello, {name}</h1>".encode())
    if path == "/hello-escaped":
        name = escape(fields.get("name", "stranger"))
        return response("200 OK", f"<h1>Hello, {name}</h1>".encode())
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
