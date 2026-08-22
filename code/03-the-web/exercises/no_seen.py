"""Exercise three: the walk without its memory.

follow.py keeps a set of the names it has already read. Take that away and
the two documents that point at each other keep the walk going forever, so
this version stops itself after a fixed number of reads.

Run it with: python3 no_seen.py
"""

import pathlib

LIBRARY = pathlib.Path(__file__).parent.parent / "library"
STOP_AFTER = 12


def read(name):
    path = LIBRARY / f"{name}.txt"
    return path.read_text() if path.exists() else None


def links_in(text):
    return [line[3:].strip() for line in text.splitlines() if line.startswith("-> ")]


to_visit = ["welcome"]
reads = 0

while to_visit and reads < STOP_AFTER:
    name = to_visit.pop(0)
    reads += 1
    print(f"{reads:>3}  {name}")
    text = read(name)
    if text is not None:
        to_visit += links_in(text)

print(f"\nstopped after {reads} reads, {len(to_visit)} names still waiting")
