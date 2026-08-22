# A model server cannot answer until its weights are read off the disk and
# into memory. Answering, once loaded, is an ordinary cheap request. So the
# reply cost stays flat while the wait to start grows with the model, and
# real weights are tens of gigabytes. That gap is why starting one of these
# servers is slow and why replacing a running one is the expensive part.
import os
import socket
import tempfile
import threading
import time


def make_file(mb):
    fd, path = tempfile.mkstemp()
    one_mb = b"\0" * (1024 * 1024)
    with os.fdopen(fd, "wb") as f:
        for _ in range(mb):
            f.write(one_mb)
    return path


def time_reply():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    port = srv.getsockname()[1]
    srv.listen(1)

    def client():
        c = socket.create_connection(("127.0.0.1", port))
        c.sendall(b"GET / HTTP/1.1\r\n\r\n")
        c.recv(4096)
        c.close()

    start = time.perf_counter()
    threading.Thread(target=client).start()
    conn, _ = srv.accept()
    conn.recv(4096)
    conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nhi")
    dt = time.perf_counter() - start
    conn.close()
    srv.close()
    return dt


print("one reply costs %.4fs, an ordinary server from chapters eight and nine"
      % time_reply())
for mb in (256, 1024):
    path = make_file(mb)
    start = time.perf_counter()
    with open(path, "rb") as f:
        weights = f.read()           # the whole file, before it can answer
    print("loading %4d MB of weights: %.3fs before it can answer anything"
          % (mb, time.perf_counter() - start))
    os.remove(path)

print("the reply never moved; the wait to start grew with the model. Real")
print("weights are tens of gigabytes, and a cold disk is slower than this,")
print("so starting is measured in minutes while the reply stays cheap.")
