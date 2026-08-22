"""Doing slow work while the visitor waits, and doing it afterwards instead.

Run it with: python3 later.py
"""

import queue
import threading
import time

sent = []


def send_the_email(address):
    """Stands in for anything slow that the visitor does not need to watch."""
    time.sleep(0.5)
    sent.append(address)


def timed(work):
    started = time.perf_counter()
    work()
    return time.perf_counter() - started


inline = timed(lambda: send_the_email("ada@example.com"))
print(f"answering after doing the work:   {inline * 1000:8.2f} ms")

# BEGIN worker
jobs = queue.Queue()


def worker():
    while True:
        address = jobs.get()
        send_the_email(address)
        jobs.task_done()


threading.Thread(target=worker, daemon=True).start()
# END worker

queued = timed(lambda: jobs.put("grace@example.com"))
print(f"answering after writing it down:  {queued * 1000:8.2f} ms")

print(f"\nemails sent so far: {sent}")
jobs.join()
print(f"emails sent once the worker caught up: {sent}")
