"""The starting half of a conversation. Run it while waiter.py is running.

Run it with:  python3 asker.py time
"""

import os
import pathlib
import sys
import time

MAILBOX = pathlib.Path(__file__).parent / "mailbox"
MAILBOX.mkdir(exist_ok=True)

question = sys.argv[1] if len(sys.argv) > 1 else "time"
request = MAILBOX / f"{os.getpid()}.request"
response = request.with_suffix(".response")

request.write_text(question)
print(f"process {os.getpid()} asked '{question}' and is now waiting")

started = time.perf_counter()
while not response.exists():
    if time.perf_counter() - started > 5:
        request.unlink(missing_ok=True)
        print("nobody answered. is waiter.py running?")
        raise SystemExit(1)
    time.sleep(0.01)

print(f"answer: {response.read_text()}")
response.unlink()
