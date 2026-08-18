"""Walk a small library of documents by following the links inside them.

Run it with: python3 follow.py
"""

import pathlib

LIBRARY = pathlib.Path(__file__).parent / "library"
START = "welcome"


def read(name):
    """The text of a document, or None if there is no such document."""
    path = LIBRARY / f"{name}.txt"
    return path.read_text() if path.exists() else None


def links_in(text):
    """Every line of a document that names another document."""
    return [line[3:].strip() for line in text.splitlines() if line.startswith("-> ")]


to_visit = [START]
seen = set()
missing = []

while to_visit:
    name = to_visit.pop(0)
    if name in seen:
        continue
    seen.add(name)

    text = read(name)
    if text is None:
        missing.append(name)
        print(f"[{name}] there is no document with this name")
        continue

    print(f"[{name}] {text.splitlines()[0]}")
    for target in links_in(text):
        print(f"          points at {target}")
        to_visit.append(target)

print(f"\ndocuments read: {len(seen) - len(missing)}")
print(f"links that point at nothing: {missing}")
