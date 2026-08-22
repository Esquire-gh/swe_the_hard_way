"""How one slow service takes down a healthy one in front of it.

Your server has a fixed pool of worker threads, from chapter thirteen.
Each request to /slow calls another service that has become slow, and
holds a worker thread for the whole wait. Fill all the workers with slow
calls and there is nobody left to serve /fast, which does no slow work at
all. The fast page stalls, and your server is not broken. The one behind
it is.

Run it with:  python3 cascade.py
"""

import concurrent.futures
import threading
import time

POOL = 4                       # the fixed number of workers, as in chapter 13
downstream_delay = 2.0         # the other service, now slow

pool = concurrent.futures.ThreadPoolExecutor(max_workers=POOL)


def slow_page():
    time.sleep(downstream_delay)      # waiting on the slow downstream service
    return "slow done"


def fast_page():
    return "fast done"                # no downstream call at all


# Fill every worker with a slow request.
slow_futures = [pool.submit(slow_page) for _ in range(POOL)]
time.sleep(0.1)

# Now a visitor asks for the fast page, which needs one free worker.
start = time.monotonic()
fast_future = pool.submit(fast_page)
fast_future.result()
waited = time.monotonic() - start

print(f"the pool has {POOL} workers, all filled with slow requests")
print(f"the fast page needed no slow work, and still waited {waited:.1f}s")
print("it waited for a worker, not for its own work: the queue backed up")
pool.shutdown()
