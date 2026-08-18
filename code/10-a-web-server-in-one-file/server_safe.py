"""A web server that reads files off the disk, and refuses to leave it.

This is server_files.py with the escape from chapter 10 closed off.

Run it with:  python3 server_safe.py
Then visit:   http://127.0.0.1:8000
Stop it with control C.
"""

import pathlib
import socket

ROOT = pathlib.Path(__file__).parent / "site"
TYPES = {".html": "text/html", ".css": "text/css", ".txt": "text/plain"}


def response(status, kind, body):
    """One HTTP response, headers and all, as bytes."""
    head = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {kind}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode() + body


# BEGIN answer
def answer(path):
    wanted = (ROOT / path.lstrip("/")).resolve()
    if ROOT.resolve() not in wanted.parents and wanted != ROOT.resolve():
        return response("403 Forbidden", "text/html", b"<h1>403 forbidden</h1>")
    if wanted.is_dir():
        wanted = wanted / "index.html"
    if not wanted.is_file():
        return response("404 Not Found", "text/html", b"<h1>404 not found</h1>")
    kind = TYPES.get(wanted.suffix, "application/octet-stream")
    return response("200 OK", kind, wanted.read_bytes())
# END answer


listening = socket.socket()
listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening.bind(("127.0.0.1", 8000))
listening.listen(5)
print(f"serving {ROOT.name}/ on http://127.0.0.1:8000")

while True:
    conversation, _ = listening.accept()
    request = conversation.recv(65536)
    path = request.split(b" ")[1].decode() if request.count(b" ") >= 2 else "/"
    print(f"asked for {path}")
    conversation.sendall(answer(path))
    conversation.close()
