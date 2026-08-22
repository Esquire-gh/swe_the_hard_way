"""Exercise three: two ways the operating system refuses a bind.

One port, one program. And ports below 1024 belong to the administrator.
Both refusals happen at bind, before anything is listening, which is the
point: the rule is enforced by the operating system rather than by
agreement between programs.

Run it with: python3 blocked_ports.py
"""

import socket

HOST = "127.0.0.1"


def try_bind(port, note):
    holder = socket.socket()
    try:
        holder.bind((HOST, port))
        holder.listen(5)
        print(f"port {port:<5} bound     {note}")
        return holder
    except OSError as refused:
        print(f"port {port:<5} refused   {type(refused).__name__}: {refused}")
        holder.close()
        return None


first = try_bind(8123, "the first program to ask gets it")
second = try_bind(8123, "this line is never reached")
eighty = try_bind(80, "the port a real web server wants")

for holder in (first, second, eighty):
    if holder is not None:
        holder.close()
