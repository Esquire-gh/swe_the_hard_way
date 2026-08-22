"""Exercise three: a shortcut inside the folder that points outside it.

The fix in server_safe.py asks where a path really lands. A symbolic
link is a file whose contents are the name of another file, so a path
that stays inside site/ the whole way can still land somewhere else.
This makes one, asks what the guard does with it, and removes it again.

Start server_safe.py first.
Run it with: python3 symlink.py
"""

import pathlib
import socket

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent / "site"
LINK = ROOT / "shortcut.txt"
TARGET = HERE.parent / "not-for-the-public.txt"


def ask(path):
    request = (f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1\r\n"
               f"Connection: close\r\n\r\n").encode()
    client_socket = socket.socket()
    try:
        client_socket.connect(("127.0.0.1", 8000))
    except ConnectionRefusedError:
        raise SystemExit("nothing on 8000: start server_safe.py first")
    client_socket.sendall(request)
    answer = b""
    while True:
        piece = client_socket.recv(4096)
        if not piece:
            break
        answer += piece
    client_socket.close()
    return answer.split(b"\r\n")[0].decode()


LINK.unlink(missing_ok=True)
LINK.symlink_to(TARGET)
here = HERE.parent.resolve()
print(f"{LINK.name} lives inside site/ and points out of it")
print(f"    asked for   site/{LINK.name}")
print(f"    lands at    {LINK.resolve().relative_to(here)}")
print(f"    inside site/? {ROOT.resolve() in LINK.resolve().parents}")

print(f"\nGET /shortcut.txt          {ask('/shortcut.txt')}")
print(f"GET /about.html            {ask('/about.html')}")

LINK.unlink()
print("\nlink removed")
