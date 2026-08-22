"""Two copies of a server behind one proxy, and the throughput that buys.

One copy has a ceiling: chapter fifteen measured it, and chapter thirteen
said why, the interpreter lock lets one process do arithmetic on one core.
Horizontal scaling is running the same program as separate processes, so
each gets its own core and its own lock. This starts the backends as real
processes, not threads, puts a round-robin proxy in front, and measures
the rate through one copy and then through two.

Run it with:  python3 horizontal.py
"""

import http.client
import socket
import subprocess
import sys
import threading
import time

BACKEND = '''
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", port))
s.listen(64)
body = b"ok\\n"
head = b"HTTP/1.1 200 OK\\r\\nContent-Length: 3\\r\\n"
reply = head + b"Connection: close\\r\\n\\r\\n" + body
while True:
    c, _ = s.accept()
    c.recv(4096)
    total = 0
    for n in range(250_000):        # about five milliseconds of real work
        total += n * n
    c.sendall(reply)
    c.close()
'''

stop = threading.Event()


def relay(visitor, target):
    try:
        up = socket.create_connection(("127.0.0.1", target))
        up.sendall(visitor.recv(4096))
        visitor.sendall(up.recv(4096))
        up.close()
    except OSError:
        pass
    visitor.close()


def proxy(front, ports):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", front))
    server.listen(128)
    server.settimeout(0.3)
    turn = 0
    while not stop.is_set():
        try:
            visitor, _ = server.accept()
        except socket.timeout:
            continue
        target = ports[turn % len(ports)]      # round-robin across the copies
        turn += 1
        threading.Thread(target=relay, args=(visitor, target),
                         daemon=True).start()
    server.close()


def measure(front, seconds=3.0):
    done = [0]
    lock = threading.Lock()
    end = threading.Event()

    def sender():
        while not end.is_set():
            try:
                conn = http.client.HTTPConnection(
                    "127.0.0.1", front, timeout=5)
                conn.request("GET", "/")
                conn.getresponse().read()
                conn.close()
                with lock:
                    done[0] += 1
            except OSError:
                pass

    senders = [threading.Thread(target=sender, daemon=True) for _ in range(20)]
    start = time.perf_counter()
    for s in senders:
        s.start()
    time.sleep(seconds)
    end.set()
    return done[0] / (time.perf_counter() - start)


backends = [subprocess.Popen([sys.executable, "-c", BACKEND, str(p)])
            for p in (8401, 8402)]
threading.Thread(target=proxy, args=(8410, [8401]), daemon=True).start()
threading.Thread(target=proxy, args=(8411, [8401, 8402]), daemon=True).start()
time.sleep(0.6)

one = measure(8410)
two = measure(8411)
print(f"through one copy:   {one:5.0f} requests per second")
print(f"through two copies: {two:5.0f} requests per second")
print(f"the second process bought about {two / one:.1f} times the throughput")

stop.set()
for b in backends:
    b.terminate()
    b.wait()
