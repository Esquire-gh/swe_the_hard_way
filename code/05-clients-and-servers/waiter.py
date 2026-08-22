"""The waiting half of a conversation. Start this first and leave it running.

Run it with:  python3 waiter.py
Stop it with control C.
"""

import os
import pathlib
import time

MAILBOX = pathlib.Path(__file__).parent / "mailbox"
MAILBOX.mkdir(exist_ok=True)

ANSWERS = {
    "time": lambda: time.strftime("%H:%M:%S"),
    "who": lambda: f"process {os.getpid()}",
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
        print(f"asked '{question}', answered '{answer}'")

    # Nothing to do, so give the processor back and look again in a moment.
    time.sleep(0.05)
