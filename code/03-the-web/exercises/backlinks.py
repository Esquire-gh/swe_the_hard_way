"""Exercise two: who links to a document?

A document knows what it points at. Nothing tells it who points back, so
the only way to answer is to read every document in the library.

Run it with: python3 backlinks.py
"""

import pathlib

LIBRARY = pathlib.Path(__file__).parent.parent / "library"


def links_in(text):
    """Every line of a document that names another document."""
    return [line[3:].strip() for line in text.splitlines() if line.startswith("-> ")]


def who_links_to(name):
    """Every document that points at `name`, and how many were read to find out."""
    found, read = [], 0
    for path in sorted(LIBRARY.glob("*.txt")):
        read += 1
        if name in links_in(path.read_text()):
            found.append(path.stem)
    return found, read


for target in ("packets", "networks", "welcome", "the-one-that-moved"):
    found, read = who_links_to(target)
    print(f"{target:<20} linked from {str(found):<26} read {read} documents")
