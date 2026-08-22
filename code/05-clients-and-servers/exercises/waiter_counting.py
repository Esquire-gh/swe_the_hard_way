"""Exercise two: a waiter that remembers.

The client exists for a fraction of a second. The server has been running
since before the first client arrived, which means it is the only half of
the pair that can remember anything. Two new questions prove it.

Start this instead of waiter.py, then ask it: python3 ../asker.py count

Run it with:  python3 waiter_counting.py
Stop it with control C.
"""

import os
import pathlib
import time

MAILBOX = pathlib.Path(__file__).parent.parent / "mailbox"
MAILBOX.mkdir(exist_ok=True)

started = time.time()
answered = 0

ANSWERS = {
    "time": lambda: time.strftime("%H:%M:%S"),
    "who": lambda: f"process {os.getpid()}",
    "count": lambda: f"{answered} question{'' if answered == 1 else 's'} so far",
    "uptime": lambda: f"{time.time() - started:.1f} seconds",
}

print(f"waiting for requests in {MAILBOX.name}/ as process {os.getpid()}")

while True:
    for request in sorted(MAILBOX.glob("*.request")):
        question = request.read_text().strip()
        if question in ANSWERS:
            answer = ANSWERS[question]()
        else:
            answer = f"I was not taught the question '{question}'"
        request.with_suffix(".response").write_text(answer)
        request.unlink()
        answered += 1
        print(f"asked '{question}', answered '{answer}'")

    time.sleep(0.05)
