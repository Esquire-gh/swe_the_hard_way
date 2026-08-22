"""Wait for a message by asking the operating system to wake you.

Run it with:            python3 blocking.py
Then in another window: python3 knock.py pipe
"""

import os
import pathlib
import time

PIPE = pathlib.Path(__file__).parent / "knock.pipe"
if not PIPE.exists():
    os.mkfifo(PIPE)

print("waiting on knock.pipe")
wall_started = time.perf_counter()
cpu_started = time.process_time()

# This line does not come back until somebody writes to the other end.
with open(PIPE) as pipe:
    message = pipe.read()

wall = time.perf_counter() - wall_started
cpu = time.process_time() - cpu_started

print(f"message: {message.strip()!r}")
print(f"waited {wall:.1f} seconds of wall clock")
print("looked 1 time, and found something")
print(f"spent {cpu:.3f} seconds of processor time doing it")
