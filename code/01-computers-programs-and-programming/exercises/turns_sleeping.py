"""Exercise one: turns.py again, with work that uses no processor.

The only change from turns.py is WORK. Sleeping is not arithmetic, so the
operating system has nothing to schedule and the count of processors stops
mattering.

Run it with: python3 turns_sleeping.py
"""

import os
import subprocess
import sys
import time

WORK = "import time; time.sleep(0.75)"


def time_copies(copies):
    started = time.perf_counter()
    running = [subprocess.Popen([sys.executable, "-c", WORK]) for _ in range(copies)]
    for process in running:
        process.wait()
    return time.perf_counter() - started


print(f"this machine reports {os.cpu_count()} processors")
for copies in (1, 2, 4, 8, 16, 32):
    print(f"{copies:>2} copies took {time_copies(copies):5.2f} seconds")
