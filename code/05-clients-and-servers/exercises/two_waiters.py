"""Exercise three: two servers, one mailbox.

Starts two copies of waiter.py on the same directory, drops a burst of
requests into it, and reports what each one did. Nothing here is unusual
code. The whole point is that the arrangement has no rule about which
copy takes a request, and under load that turns into a crash.

Run it with:  python3 two_waiters.py
"""

import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
MAILBOX = HERE.parent / "mailbox"
WAITER = HERE.parent / "waiter.py"
BURST = 300

for stale in MAILBOX.glob("*"):
    stale.unlink()
MAILBOX.mkdir(exist_ok=True)

waiters = [subprocess.Popen([sys.executable, "-u", str(WAITER)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True)
           for _ in range(2)]
time.sleep(1.0)

for n in range(BURST):
    (MAILBOX / f"{n}.request").write_text("time")
time.sleep(2.0)

for number, waiter in enumerate(waiters, start=1):
    waiter.terminate()
    output = waiter.communicate()[0]
    answered = sum(1 for line in output.splitlines() if line.startswith("asked"))
    died = "Traceback" in output
    print(f"waiter {number}: answered {answered:>3} of {BURST}"
          f"{'   and then died' if died else ''}")
    if died:
        print("   " + output.strip().splitlines()[-1])

for leftover in MAILBOX.glob("*"):
    leftover.unlink()
