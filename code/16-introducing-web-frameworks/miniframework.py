"""The forty lines that make "you do not call a framework" literal.

A framework is a registry plus a loop. The decorator records which
function answers which method and path. The loop, built on chapter
eleven's socket code, reads a request, finds the matching function,
pulls {number} out of the path, converts it using the function's own type
annotation, and calls it. Your functions never call this file. This file
calls them, which is the whole difference the chapter is about.

Run it with:  python3 miniframework.py
Then, from another window:  curl -s http://127.0.0.1:8400/messages/3
"""

import inspect
import socket

routes = []          # (method, [path parts], function, annotations)


def route(method, pattern):
    def remember(function):
        parts = pattern.strip("/").split("/")
        routes.append((method, parts, function, function.__annotations__))
        return function
    return remember


def match(method, path):
    """Find a route, and pull the values out of the path it names."""
    wanted = path.strip("/").split("/")
    for route_method, parts, function, annotations in routes:
        if route_method != method or len(parts) != len(wanted):
            continue
        values = {}
        for part, given in zip(parts, wanted):
            if part.startswith("{") and part.endswith("}"):
                values[part[1:-1]] = given          # a captured piece
            elif part != given:
                break
        else:
            return function, annotations, values
    return None, None, None


def call(function, annotations, values):
    """Convert each captured value by its annotation, then call."""
    for name, value in values.items():
        converter = annotations.get(name, str)
        values[name] = converter(value)             # "3" -> 3, by int
    return function(**values)


def reply(status, body):
    head = (f"HTTP/1.1 {status}\r\nContent-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n")
    return head.encode() + body.encode()


# ---- an application, written the way a framework lets you write one ----
@route("GET", "/")
def home():
    return "the guestbook"


@route("GET", "/messages/{number}")
def one_message(number: int):
    return f"message {number}, and {number} is a real int: {number + 1}"


def serve():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 8400))
    server.listen(16)
    print("mini-framework on http://127.0.0.1:8400")
    while True:
        connection, _ = server.accept()
        request = connection.recv(65536).decode(errors="replace")
        method, path, *_ = request.split(" ") + ["", ""]
        function, annotations, values = match(method, path)
        if function is None:
            connection.sendall(reply("404 Not Found", "no such route\n"))
        else:
            try:
                connection.sendall(reply("200 OK", call(function, annotations,
                                                        values) + "\n"))
            except ValueError:
                connection.sendall(reply("422 Unprocessable Content",
                                         "a path value was the wrong type\n"))
        connection.close()


if __name__ == "__main__":
    serve()
