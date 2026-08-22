"""The obvious answer to losing everything on restart: write it down.

Run it with: python3 to_a_file.py
"""

import json
import pathlib

BOOK = pathlib.Path(__file__).parent / "guestbook.json"


def load():
    """Every message written so far, or none if there is no file yet."""
    if not BOOK.exists():
        return []
    return json.loads(BOOK.read_text())


def add(who, text):
    messages = load()
    messages.append({"who": who, "text": text})
    BOOK.write_text(json.dumps(messages))


add("Ada", "first")
add("Grace", "second")

print(f"the file is {BOOK.stat().st_size} bytes")
for message in load():
    print(f"  {message['who']}: {message['text']}")
