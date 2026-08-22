"""What a thread actually costs, measured on this machine.

The threaded server starts one thread per visitor, so the number of
visitors you can hold is decided by what a thread costs. This starts a
thousand threads that do nothing but sleep, and measures the memory the
process grew by. The reserved stack for each thread is larger than this,
often near a megabyte, but reserved is not the same as used.

Run it with:  python3 thread_cost.py
"""

import resource
import sys
import threading
import time

HOW_MANY = 1000


def resident_mb():
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes here; Linux reports kilobytes.
    return peak / 1_000_000 if sys.platform == "darwin" else peak / 1000


before = resident_mb()
gate = threading.Event()
threads = [threading.Thread(target=gate.wait) for _ in range(HOW_MANY)]
for thread in threads:
    thread.start()
time.sleep(1.0)
after = resident_mb()

print(f"{HOW_MANY} sleeping threads")
print(f"    memory before   {before:6.1f} MB")
print(f"    memory after    {after:6.1f} MB")
each = (after - before) * 1000 / HOW_MANY
print(f"    each thread     {each:6.1f} KB resident")

gate.set()
for thread in threads:
    thread.join()
