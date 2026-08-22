"""Find the requests per second of a server, and where it falls over.

Scaling talk is empty without a number to start from. This throws requests
at a server as fast as a fixed pool of senders can, counts how many
succeed in a few seconds, and reports the rate. Point it at chapter
thirteen's one-at-a-time server and then at the threaded one, and the
difference stops being a claim.

Start a server on 8200 first, for example:
    python3 ../13-handling-multiple-users-at-once/one_at_a_time_threaded.py
Then run:  python3 load.py
"""

import http.client
import threading
import time

HOST = ("127.0.0.1", 8200)
SENDERS = 20
SECONDS = 3.0

done = 0
failed = 0
lock = threading.Lock()
stop = threading.Event()


def sender():
    global done, failed
    while not stop.is_set():
        try:
            conn = http.client.HTTPConnection(*HOST, timeout=5)
            conn.request("GET", "/work")
            conn.getresponse().read()
            conn.close()
            with lock:
                done += 1
        except OSError:
            with lock:
                failed += 1


threads = [threading.Thread(target=sender, daemon=True)
           for _ in range(SENDERS)]
start = time.perf_counter()
for thread in threads:
    thread.start()
time.sleep(SECONDS)
stop.set()
elapsed = time.perf_counter() - start

print(f"{SENDERS} senders for {SECONDS:.0f}s against {HOST[0]}:{HOST[1]}/work")
print(f"    answered   {done}")
print(f"    failed     {failed}")
print(f"    rate       {done / elapsed:.0f} requests per second")
