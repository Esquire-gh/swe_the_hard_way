"""Exercise one: does 127.0.0.1 keep out of 0.0.0.0's way?

0.0.0.0 does not mean one address. It means every address this machine
has, including 127.0.0.1. So a socket bound to 0.0.0.0:8000 already owns
127.0.0.1:8000, and a second socket asking for 127.0.0.1:8000 is asking
for something already taken. This shows it both ways round.

Run it with:  python3 two_addresses.py
"""

import socket

PORT = 8210


def bind(host):
    sock = socket.socket()
    try:
        sock.bind((host, PORT))
        sock.listen(1)
        return sock, "ok"
    except OSError as why:
        return None, f"{type(why).__name__}: {why.strerror}"


first, msg = bind("0.0.0.0")
print(f"bind 0.0.0.0:{PORT}     {msg}")
second, msg = bind("127.0.0.1")
print(f"bind 127.0.0.1:{PORT}   {msg}   <- covered by 0.0.0.0 above")

for sock in (first, second):
    if sock:
        sock.close()

print("\nthe reverse is also true: bind 127.0.0.1 first and 0.0.0.0 is")
print("refused, because 0.0.0.0 includes the address 127.0.0.1 holds.")
