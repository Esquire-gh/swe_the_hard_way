"""Three ways the file from to_a_file.py loses data once anybody else is using
it.

Run it with: python3 lost_and_truncated.py
"""

import json
import pathlib
import threading
import time

BOOK = pathlib.Path(__file__).parent / "racy.json"
WRITERS = 4
EACH = 50

unreadable = 0


def add(who, text):
    """Read the whole book, add one line, write the whole book back."""
    global unreadable
    try:
        messages = json.loads(BOOK.read_text())
    except json.JSONDecodeError:
        unreadable += 1          # somebody was halfway through writing it
        return
    time.sleep(0)                # the same handing over as chapter 14
    messages.append({"who": who, "text": text})
    BOOK.write_text(json.dumps(messages))


def writer(number):
    for line in range(EACH):
        add(f"writer {number}", str(line))


BOOK.write_text("[]")
threads = [threading.Thread(target=writer, args=(n,)) for n in range(WRITERS)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(f"messages the program tried to write: {WRITERS * EACH}")
print(f"times a reader found the file half written: {unreadable}")
try:
    print(f"messages actually in the file: {len(json.loads(BOOK.read_text()))}")
except json.JSONDecodeError as damage:
    print(f"the finished file is not valid at all: {damage}")

# Opening a file for writing empties it before anything is written.
print(f"\nthe file is {BOOK.stat().st_size} bytes")
try:
    with open(BOOK, "w") as book:
        raise KeyboardInterrupt("the machine lost power here")
except KeyboardInterrupt as stopped:
    print(f"interrupted: {stopped}")
print(f"the file is now {BOOK.stat().st_size} bytes")
BOOK.unlink()
