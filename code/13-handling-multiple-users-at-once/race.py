"""Four threads adding to the same number, with and without a lock.

Run it with: python3 race.py
"""

import threading
import time

WORKERS = 4


def count(adds, lock=None, hand_over=False):
    """Every worker adds `adds` to one shared total."""
    total = 0

    def worker():
        nonlocal total
        for _ in range(adds):
            if lock:
                lock.acquire()
            current = total            # read
            if hand_over:
                time.sleep(0)          # let another thread have a turn here
            total = current + 1        # write
            if lock:
                lock.release()

    threads = [threading.Thread(target=worker) for _ in range(WORKERS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return total


for adds, lock, hand_over, label in [
    (100_000, None, False, "no lock"),
    (5_000, None, True, "no lock, switching often"),
    (5_000, threading.Lock(), True, "with a lock"),
]:
    print(f"{label:<26} wanted {adds * WORKERS:>7}   got {count(adds, lock, hand_over):>7}")
