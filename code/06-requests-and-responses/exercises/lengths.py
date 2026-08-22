"""Exercise one: what a wrong Content-Length does to the next message.

The parser has one way of knowing where the body ends: it believes the
number in the header. Change the number and watch what the next reader
inherits.

Run it with: python3 lengths.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from parse import parse                                   # noqa: E402

TEMPLATE = (
    "POST /search HTTP/1.1\r\n"
    "Host: example.com\r\n"
    "Content-Length: {length}\r\n"
    "\r\n"
    "q=packets\r\n"
)


def two_messages(length):
    """Two identical requests back to back, both claiming this length."""
    return (TEMPLATE.format(length=length) * 2).encode()


for length in (11, 9, 20):
    first, headers, body, leftover = parse(two_messages(length))
    print(f"Content-Length: {length}")
    print(f"    body      {body!r}  ({len(body)} bytes)")
    print(f"    left over {len(leftover)} bytes")

    second = parse(leftover)[0]
    reported = " | ".join(part.decode() for part in second)
    print(f"    the next reader sees a first line of: {reported!r}\n")
