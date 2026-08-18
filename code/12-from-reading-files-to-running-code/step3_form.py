"""Accepting something the visitor typed, and remembering it while we run.

Run it with:  python3 step3_form.py
Then visit:   http://127.0.0.1:8000/
Stop it with control C.
"""

import socket
from urllib.parse import unquote_plus

messages = []


def response(status, body, kind="text/html", extra=()):
    lines = [f"HTTP/1.1 {status}", f"Content-Type: {kind}",
             f"Content-Length: {len(body)}", "Connection: close", *extra]
    return ("\r\n".join(lines) + "\r\n\r\n").encode() + body


def redirect(where):
    lines = [f"HTTP/1.1 303 See Other", f"Location: {where}",
             "Content-Length: 0", "Connection: close"]
    return ("\r\n".join(lines) + "\r\n\r\n").encode()


def escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def parse_fields(text):
    """Fields written as name=value&name=value, in a query or in a body."""
    fields = {}
    for pair in text.split("&"):
        if not pair:
            continue
        name, _, value = pair.partition("=")
        fields[unquote_plus(name)] = unquote_plus(value)
    return fields


def read_request(conversation):
    """Read one whole request off the connection, headers and body."""
    data = conversation.recv(65536)
    head, separator, rest = data.partition(b"\r\n\r\n")
    if not separator:
        return head, b""

    length = 0
    for line in head.split(b"\r\n")[1:]:
        name, _, value = line.partition(b": ")
        if name.lower() == b"content-length":
            length = int(value)

    while len(rest) < length:          # the body may not have all arrived yet
        rest += conversation.recv(65536)
    return head, rest[:length]


def page():
    items = "".join(f"<li>{escape(one)}</li>" for one in messages)
    return f"""<!doctype html>
<h1>Guestbook</h1>
<ul>{items or "<li>nothing yet</li>"}</ul>
<form method="post" action="/messages">
  <input name="message"><button>sign</button>
</form>
""".encode()


def handle(head, body):
    method, target, _ = head.split(b"\r\n")[0].decode().split(" ")
    path, _, query = target.partition("?")

    if method == "GET" and path == "/":
        return response("200 OK", page())
    if method == "POST" and path == "/messages":
        text = parse_fields(body.decode()).get("message", "").strip()
        if text:
            messages.append(text)
        return redirect("/")
    if path in ("/", "/messages"):
        return response("405 Method Not Allowed", b"<h1>405 not allowed</h1>")
    return response("404 Not Found", b"<h1>404 not found</h1>")


listening = socket.socket()
listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening.bind(("127.0.0.1", 8000))
listening.listen(5)
print("listening on http://127.0.0.1:8000")

while True:
    conversation, _ = listening.accept()
    conversation.sendall(handle(*read_request(conversation)))
    conversation.close()
