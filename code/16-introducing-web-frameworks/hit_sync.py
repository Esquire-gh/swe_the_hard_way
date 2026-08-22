"""Five requests at once to a def route, to see the thread pool.

Run thread_names under uvicorn first:
    .venv/bin/uvicorn thread_names:app --port 8000
Then run:  python3 hit_sync.py
"""

import http.client
import json
import threading

ids = []
lock = threading.Lock()


def hit():
    conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=5)
    conn.request("GET", "/sync")
    answer = json.loads(conn.getresponse().read())
    with lock:
        ids.append(answer["id"])
    conn.close()


threads = [threading.Thread(target=hit) for _ in range(5)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print("five concurrent /sync requests ran on these thread ids:")
for thread_id in sorted(set(ids)):
    print(f"    {thread_id}")
print(f"distinct threads: {len(set(ids))}")
