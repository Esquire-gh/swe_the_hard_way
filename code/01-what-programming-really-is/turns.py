"""Run the same fixed amount of work in one process, then in many at once.

Run it with: python3 turns.py
"""

import os
import subprocess
import sys
import time

# Enough adding up to take a noticeable moment and nothing else.
WORK = "sum(range(100_000_000))"


def time_copies(copies):
    """Start this many copies at once and wait for all of them to finish."""
    started = time.perf_counter()
    running = [subprocess.Popen([sys.executable, "-c", WORK]) for _ in range(copies)]
    for process in running:
        process.wait()
    return time.perf_counter() - started


print(f"this machine reports {os.cpu_count()} processors")
for copies in (1, 2, 4, 8, 16, 32):
    print(f"{copies:>2} copies took {time_copies(copies):5.2f} seconds")
