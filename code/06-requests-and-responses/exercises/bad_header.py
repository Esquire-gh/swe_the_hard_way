"""Exercise three: a header line with no colon in it.

The parser splits each header on the first ": ". A line without one does
not raise anything. It becomes a header whose name is the whole line and
whose value is empty, and the request is accepted as if nothing happened.

Run it with: python3 bad_header.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from parse import parse                                   # noqa: E402

BROKEN = (
    b"GET /account HTTP/1.1\r\n"
    b"Host: example.com\r\n"
    b"Content-Length 4\r\n"                # the colon is missing
    b"\r\n"
    b"halt"
)


def strict(raw):
    """The same split, refusing anything it cannot understand."""
    head, _, rest = raw.partition(b"\r\n\r\n")
    lines = head.split(b"\r\n")
    for line in lines[1:]:
        if b": " not in line:
            raise ValueError(f"header line has no colon: {line!r}")
    return parse(raw)


first, headers, body, leftover = parse(BROKEN)
print("what the forgiving parser did:")
print(f"    headers    {headers}")
print(f"    body       {body!r}")
print(f"    left over  {leftover!r}")

print("\nwhat the strict parser does:")
try:
    strict(BROKEN)
except ValueError as problem:
    print(f"    refused: {problem}")
    print("    a server would answer 400 Bad Request and close the connection")
