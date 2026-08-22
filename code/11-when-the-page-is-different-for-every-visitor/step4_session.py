"""Remembering who a visitor is across separate connections.

Run it with:  python3 step4_session.py
Then visit:   http://127.0.0.1:8000/
Stop it with control C.
"""

import secrets
import socket
from urllib.parse import unquote_plus

messages = []
sessions = {}          # session id -> the name that session belongs to


def response(status, body, kind="text/html", extra=()):
    lines = [f"HTTP/1.1 {status}", f"Content-Type: {kind}",
             f"Content-Length: {len(body)}", "Connection: close", *extra]
    return ("\r\n".join(lines) + "\r\n\r\n").encode() + body


def redirect(where, extra=()):
    lines = ["HTTP/1.1 303 See Other", f"Location: {where}",
             "Content-Length: 0", "Connection: close", *extra]
    return ("\r\n".join(lines) + "\r\n\r\n").encode()


def escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def parse_fields(text):
    fields = {}
    for pair in text.split("&"):
        if not pair:
            continue
        name, _, value = pair.partition("=")
        fields[unquote_plus(name)] = unquote_plus(value)
    return fields


def headers_of(head):
    found = {}
    for line in head.split(b"\r\n")[1:]:
        name, _, value = line.partition(b": ")
        found[name.decode().lower()] = value.decode()
    return found


# BEGIN cookies
def cookies_of(headers):
    found = {}
    for pair in headers.get("cookie", "").split(";"):
        name, _, value = pair.strip().partition("=")
        if name:
            found[name] = value
    return found
# END cookies


def read_request(conversation):
    data = conversation.recv(65536)
    head, separator, rest = data.partition(b"\r\n\r\n")
    if not separator:
        return head, b""
    length = int(headers_of(head).get("content-length", 0))
    while len(rest) < length:
        rest += conversation.recv(65536)
    return head, rest[:length]


def sign_in_page():
    return b"""<!doctype html>
<h1>Guestbook</h1>
<p>Say who you are before signing.</p>
<form method="post" action="/login">
  <input name="name"><button>continue</button>
</form>
"""


def guestbook_page(name):
    items = "".join(f"<li>{escape(who)}: {escape(text)}</li>"
                    for who, text in messages)
    return f"""<!doctype html>
<h1>Guestbook</h1>
<p>Signed in as {escape(name)}.</p>
<ul>{items or "<li>nothing yet</li>"}</ul>
<form method="post" action="/messages">
  <input name="message"><button>sign</button>
</form>
""".encode()


def handle(head, body):
    method, target, _ = head.split(b"\r\n")[0].decode().split(" ")
    path, _, query = target.partition("?")
    headers = headers_of(head)
    who = sessions.get(cookies_of(headers).get("session", ""))

    if method == "GET" and path == "/":
        return response("200 OK", guestbook_page(who) if who else sign_in_page())

# BEGIN login
    if method == "POST" and path == "/login":
        name = parse_fields(body.decode()).get("name", "").strip()
        if not name:
            return redirect("/")
        token = secrets.token_hex(16)
        sessions[token] = name
        return redirect("/", [f"Set-Cookie: session={token}; Path=/; HttpOnly"])
# END login

    if method == "POST" and path == "/messages":
        if not who:
            return redirect("/")
        text = parse_fields(body.decode()).get("message", "").strip()
        if text:
            messages.append((who, text))
        return redirect("/")

    if path in ("/", "/login", "/messages"):
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
