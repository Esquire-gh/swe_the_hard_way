"""Exercise three: one port, two programs, on purpose.

Chapter twelve says a port holds one program. That is a rule the operating
system enforces, not a law of physics, and the operating system has a
switch that turns it off. With SO_REUSEPORT set on both sockets, two of
them bind the same port, and the kernel hands each new connection to one
of them. This is how a server runs several identical worker processes
behind one port with nothing in front of them.

Run it with:  python3 reuseport.py
"""

import socket

PORT = 8211
REUSEPORT = getattr(socket, "SO_REUSEPORT", None)

if REUSEPORT is None:
    raise SystemExit("this operating system has no SO_REUSEPORT")


def bind(with_switch):
    sock = socket.socket()
    if with_switch:
        sock.setsockopt(socket.SOL_SOCKET, REUSEPORT, 1)
    try:
        sock.bind(("127.0.0.1", PORT))
        sock.listen(1)
        return sock, "ok"
    except OSError as why:
        return None, f"{type(why).__name__}: {why.strerror}"


print("without the switch:")
a, msg = bind(False)
print(f"    first  {msg}")
b, msg = bind(False)
print(f"    second {msg}   <- the rule you already know")
for sock in (a, b):
    if sock:
        sock.close()

print("\nwith SO_REUSEPORT on both:")
c, msg = bind(True)
print(f"    first  {msg}")
d, msg = bind(True)
print(f"    second {msg}   <- the same port, twice, allowed")
for sock in (c, d):
    if sock:
        sock.close()
