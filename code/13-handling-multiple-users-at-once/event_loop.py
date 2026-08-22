"""One thread holding every connection, with no threads at all.

Instead of a thread per visitor, one thread asks the operating system
which connections have something ready right now, and does a small piece
of work on each. This is the third answer the title promises. It reaches
huge numbers of connections on one thread, and its weakness is the mirror
of its strength: any slow piece of work stops everything, because there is
only one thread to stop.

Run it with:  python3 event_loop.py
Then visit:   http://127.0.0.1:8200/
Stop it with control C.
"""

import selectors
import socket

selector = selectors.DefaultSelector()
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 8200))
server.listen(128)
server.setblocking(False)
selector.register(server, selectors.EVENT_READ, data="server")

BODY = b"served by one thread, no threads\n"
REPLY = (b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\n"
         b"Connection: close\r\n\r\n" % len(BODY)) + BODY

print("listening on http://127.0.0.1:8200, one thread")
while True:
    for key, _ in selector.select():          # ready connections only
        if key.data == "server":
            connection, _ = server.accept()   # a new visitor
            connection.setblocking(False)
            selector.register(connection, selectors.EVENT_READ, data="client")
        else:
            connection = key.fileobj
            connection.recv(65536)            # the request, ignored here
            connection.sendall(REPLY)
            selector.unregister(connection)
            connection.close()
