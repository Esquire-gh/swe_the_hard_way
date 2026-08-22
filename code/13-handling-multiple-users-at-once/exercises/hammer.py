"""Four hundred requests to /count, twenty at a time, then read the total.

If the counter were correct the server would report 400. Without the lock
in count_server.py it reports fewer, because requests that ran at the same
instant read the same number and wrote the same number back.

Run count_server.py first, then:  python3 hammer.py
"""

import http.client
import threading

HOST, ROUNDS, AT_ONCE = ("127.0.0.1", 8200), 20, 20


def one():
    conn = http.client.HTTPConnection(*HOST)
    conn.request("GET", "/count")
    conn.getresponse().read()
    conn.close()


for _ in range(ROUNDS):
    batch = [threading.Thread(target=one) for _ in range(AT_ONCE)]
    for thread in batch:
        thread.start()
    for thread in batch:
        thread.join()

conn = http.client.HTTPConnection(*HOST)
conn.request("GET", "/")
total = conn.getresponse().read().decode().strip()
print(total, "  (should be: hits so far: 400)")
conn.close()
