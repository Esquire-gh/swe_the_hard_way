"""Exercise three: what two hundred waiting programs cost.

Starts a crowd of processes that all wait the same way, lets them wait,
then adds up the processor time they used between them. One poller is
cheap. The question is what a machine full of them costs.

Run it with:  python3 many_waiters.py polling
          or: python3 many_waiters.py blocking
"""

import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
HOW_MANY = 200
SECONDS = 10.0
GAP = 0.005                      # the polling interval, five milliseconds


def worker(how, number):
    """One waiting process. Prints the processor time it used."""
    flag = HERE / "crowd" / f"{number}.knock"
    pipe = HERE / "crowd" / f"{number}.pipe"
    started = time.process_time()
    if how == "polling":
        while not flag.exists():
            time.sleep(GAP)
    else:
        if not pipe.exists():
            os.mkfifo(pipe)
        with open(pipe) as open_pipe:
            open_pipe.read()
    print(f"{time.process_time() - started:.4f}")


if len(sys.argv) > 2 and sys.argv[1] == "--worker":
    worker(sys.argv[2], int(sys.argv[3]))
    raise SystemExit

how = sys.argv[1] if len(sys.argv) > 1 else "polling"
crowd = HERE / "crowd"
crowd.mkdir(exist_ok=True)
for old in crowd.iterdir():
    old.unlink()

started = time.perf_counter()
waiters = [subprocess.Popen(
    [sys.executable, str(HERE / "many_waiters.py"), "--worker", how, str(n)],
    stdout=subprocess.PIPE, text=True) for n in range(HOW_MANY)]

time.sleep(SECONDS)

for n in range(HOW_MANY):                        # wake them all
    if how == "polling":
        (crowd / f"{n}.knock").write_text("go")
    else:
        with open(crowd / f"{n}.pipe", "w") as pipe:
            pipe.write("go")

used = sum(float(waiter.communicate()[0].strip()) for waiter in waiters)
wall = time.perf_counter() - started

for leftover in crowd.iterdir():
    leftover.unlink()
crowd.rmdir()

print(f"{HOW_MANY} processes waiting the {how} way for {SECONDS:.0f} seconds")
print(f"    wall clock            {wall:.1f} seconds")
print(f"    processor time used   {used:.2f} seconds")
print(f"    that is {used / wall:.2f} of one processor, spent on nothing")
