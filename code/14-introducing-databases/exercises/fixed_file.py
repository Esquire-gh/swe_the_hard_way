"""Fix the file from lost_and_truncated.py, by hand, until 200 of 200 land.

Two of the three failures have a fix you can write. A reader never sees a
half written file if you write a new file and rename it over the old one,
because a rename is one step the filesystem either finishes or does not. Two
writers never overwrite each other if they take a lock first. This does both,
runs the same four writers, and counts what survives.

Run it with:  python3 fixed_file.py
"""

import json
import os
import pathlib
import threading

BOOK = pathlib.Path(__file__).parent / "fixed.json"
WRITERS, EACH = 4, 50
lock = threading.Lock()


def add(who, text):
    with lock:                              # one writer at a time
        messages = json.loads(BOOK.read_text())
        messages.append({"who": who, "text": text})
        temporary = BOOK.with_suffix(".tmp")
        temporary.write_text(json.dumps(messages))
        os.replace(temporary, BOOK)   # one step: old or new, never half


def writer(number):
    for line in range(EACH):
        add(f"writer {number}", str(line))


BOOK.write_text("[]")
threads = [threading.Thread(target=writer, args=(n,)) for n in range(WRITERS)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

stored = len(json.loads(BOOK.read_text()))
print(f"messages the program tried to write: {WRITERS * EACH}")
print(f"messages actually in the file: {stored}")
BOOK.unlink()
