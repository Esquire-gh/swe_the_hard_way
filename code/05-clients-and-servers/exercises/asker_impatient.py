"""Exercise two, the other half: a client that gives up sooner.

asker.py waits five seconds. Nothing about five is special, and the number
is the client's decision alone: the server is never told about it and has
no way to ask for more time.

Run it with:  python3 asker_impatient.py count 0.5
"""

import os
import pathlib
import sys
import time

MAILBOX = pathlib.Path(__file__).parent.parent / "mailbox"
MAILBOX.mkdir(exist_ok=True)

question = sys.argv[1] if len(sys.argv) > 1 else "time"
deadline = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

request = MAILBOX / f"{os.getpid()}.request"
response = request.with_suffix(".response")

request.write_text(question)
print(f"process {os.getpid()} asked '{question}', waiting up to {deadline}s")

started = time.perf_counter()
while not response.exists():
    if time.perf_counter() - started > deadline:
        request.unlink(missing_ok=True)
        print(f"gave up after {deadline}s")
        raise SystemExit(1)
    time.sleep(0.01)

print(f"answer: {response.read_text()}   (waited {time.perf_counter() - started:.3f}s)")
response.unlink()
