"""Two processes, two in-memory caches, and one visitor who sees both.

A cache inside your process belongs to that process alone. Run two copies
of your server behind a load balancer, as this chapter's deploy did, and
you have two caches that do not know about each other. This starts two
worker processes, has each cache the current time on first request, waits,
and asks each one. They disagree, because each remembered its own moment.

Run it with:  python3 two_caches.py
"""

import subprocess
import sys
import time

WORKER = '''
import time
cache = {}
def answer():
    if "t" not in cache:
        cache["t"] = time.strftime("%H:%M:%S")
    return cache["t"]
print(answer(), flush=True)   # first request: fills this process's cache
import sys; sys.stdin.readline()
print(answer(), flush=True)   # later request: same process, same cached value
'''


def start():
    return subprocess.Popen([sys.executable, "-c", WORKER],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            text=True)


one = start()
time.sleep(1.2)               # let the two caches fill a second apart
two = start()

first_of_one = one.stdout.readline().strip()
first_of_two = two.stdout.readline().strip()
one.stdin.write("\n"); one.stdin.flush()
two.stdin.write("\n"); two.stdin.flush()
later_of_one = one.stdout.readline().strip()
later_of_two = two.stdout.readline().strip()
one.wait(); two.wait()

print(f"process one cached: {first_of_one}, and still says {later_of_one}")
print(f"process two cached: {first_of_two}, and still says {later_of_two}")
print("a visitor sent to one process, then the other, sees two answers")
