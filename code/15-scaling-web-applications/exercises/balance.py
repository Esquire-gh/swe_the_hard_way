"""Two copies behind one proxy, one killed mid-run, and no failed request.

This is the deploy and the supervisor put together. Two backends run
behind a proxy that spreads requests across whichever are healthy. One
backend is killed with SIGKILL partway through a steady stream of
requests. A proxy that balanced blindly would send every other request
into the void; this one checks health and stops using the dead one, so
the visitor never sees a failure.

Run it with:  python3 balance.py
"""

import http.client
import signal
import socket
import subprocess
import sys
import threading
import time

FRONT = ("127.0.0.1", 8320)
BACKENDS = [("127.0.0.1", 8321), ("127.0.0.1", 8322)]
healthy = {b: True for b in BACKENDS}
served, failed = 0, 0
stop = threading.Event()
callers_stop = threading.Event()

BACKEND_CODE = '''
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", port))
s.listen(16)
body = ("from %d\\n" % port).encode()
head = b"HTTP/1.1 200 OK\\r\\nContent-Length: %d\\r\\n" % len(body)
reply = head + b"Connection: close\\r\\n\\r\\n" + body
while True:
    c, _ = s.accept()
    c.recv(4096)
    c.sendall(reply)
    c.close()
'''


def health_poller():
    while not stop.is_set():
        for b in BACKENDS:
            try:
                probe = socket.create_connection(b, timeout=0.2)
                probe.close()
                healthy[b] = True
            except OSError:
                healthy[b] = False
        time.sleep(0.1)


def proxy():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(FRONT)
    server.listen(64)
    server.settimeout(0.3)
    turn = 0
    while not stop.is_set():
        try:
            visitor, _ = server.accept()
        except socket.timeout:
            continue
        request = visitor.recv(4096)
        for attempt in range(len(BACKENDS)):
            live = [b for b in BACKENDS if healthy[b]]
            if not live:
                break
            target = live[turn % len(live)]  # spread across the healthy ones
            turn += 1
            try:
                up = socket.create_connection(target, timeout=0.3)
                up.sendall(request)
                visitor.sendall(up.recv(4096))
                up.close()
                break                        # served; done with this visitor
            except OSError:
                healthy[target] = False      # it just died; try another one
        visitor.close()
    server.close()


def caller():
    global served, failed
    while not callers_stop.is_set():
        try:
            conn = http.client.HTTPConnection(*FRONT, timeout=2)
            conn.request("GET", "/")
            conn.getresponse().read()
            conn.close()
            served += 1
        except OSError:
            failed += 1
        time.sleep(0.003)


procs = [subprocess.Popen([sys.executable, "-c", BACKEND_CODE, str(port)])
         for _, port in BACKENDS]
time.sleep(0.4)
threading.Thread(target=health_poller, daemon=True).start()
threading.Thread(target=proxy, daemon=True).start()
time.sleep(0.3)

callers = [threading.Thread(target=caller, daemon=True) for _ in range(5)]
for thread in callers:
    thread.start()

time.sleep(0.6)
print("killing one backend with SIGKILL, mid-stream")
procs[0].send_signal(signal.SIGKILL)
procs[0].wait()
time.sleep(0.8)

callers_stop.set()
time.sleep(0.3)
stop.set()
time.sleep(0.5)
for proc in procs:
    if proc.poll() is None:
        proc.terminate()
        proc.wait()

print(f"requests served: {served}")
print(f"requests failed: {failed}")
