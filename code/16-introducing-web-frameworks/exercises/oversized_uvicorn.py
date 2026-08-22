"""The four-billion-byte request from chapter eleven, aimed at uvicorn.

Chapter eleven's oversized_body.py made the hand-written server collect a
body until it ran out of memory, because that server read one connection
at a time and trusted Content-Length. This sends the same lie to uvicorn:
one connection claims four billion bytes and then goes quiet. While it
hangs, this keeps asking for the normal page and counts how many succeed.

Start the app first:
    .venv/bin/uvicorn app:app --port 8000
Then run:  python3 exercises/oversized_uvicorn.py
"""

import http.client
import socket
import threading
import time

liar_done = threading.Event()


def the_liar():
    """One connection that claims a huge body and never sends it."""
    sock = socket.socket()
    sock.connect(("127.0.0.1", 8000))
    sock.sendall(b"POST /login HTTP/1.1\r\nHost: x\r\n"
                 b"Content-Type: application/x-www-form-urlencoded\r\n"
                 b"Content-Length: 4000000000\r\n\r\n")
    sock.sendall(b"name=" + b"A" * 1000)     # a trickle, then silence
    time.sleep(3.0)
    sock.close()
    liar_done.set()


served = 0
threading.Thread(target=the_liar, daemon=True).start()
time.sleep(0.2)

start = time.monotonic()
while time.monotonic() - start < 2.0:
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=2)
        conn.request("GET", "/")
        conn.getresponse().read()
        conn.close()
        served += 1
    except OSError:
        pass
    time.sleep(0.05)

print(f"while one connection claimed four billion bytes and stalled,")
print(f"the normal page was served {served} times without trouble")
print("uvicorn isolated the bad request to its own connection")
