"""Exercise three: run the script yourself, in a real browser.

The chapter shows curl printing a script tag back. curl does not run it,
so nothing appears to happen. A browser runs it. This server hands out
two cookies that differ in one word, and has one page that forgets to
escape, so you can see what a script injected into your page can reach
and what it cannot.

Run it with:   python3 cookie_theft.py
Then visit:    http://127.0.0.1:8000/login
Then visit:    http://127.0.0.1:8000/hello?name=YOUR+SCRIPT+HERE
Stop it with control C.
"""

import secrets
import socket

sessions = {}


def response(status, body, extra=()):
    lines = ["HTTP/1.1 " + status, "Content-Type: text/html",
             f"Content-Length: {len(body)}", "Connection: close", *extra]
    return ("\r\n".join(lines) + "\r\n\r\n").encode() + body


def handle(request):
    first = request.split(b"\r\n")[0].decode()
    method, target, _ = first.split(" ")
    path, _, query = target.partition("?")

    if path == "/login":
        token = secrets.token_hex(8)
        sessions[token] = "Ada"
        return response("200 OK", b"<h1>Signed in</h1><p>Two cookies set."
                        b" Now visit /hello with a script in the name.</p>",
                        [f"Set-Cookie: session={token}; Path=/; HttpOnly",
                         f"Set-Cookie: visitor={token}; Path=/"])

    if path == "/hello":
        from urllib.parse import unquote_plus
        name = "stranger"
        for pair in query.split("&"):
            if pair.startswith("name="):
                name = unquote_plus(pair[5:])
        # The bug, on purpose: name goes in unchanged.
        page = f"<h1>Hello, {name}</h1><p>Anything below is not ours.</p>"
        return response("200 OK", page.encode())

    return response("404 Not Found", b"<h1>404 not found</h1>")


server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", 8000))
server_socket.listen(5)
print("listening on http://127.0.0.1:8000")

while True:
    connection, _ = server_socket.accept()
    connection.sendall(handle(connection.recv(65536)))
    connection.close()
