"""Turn names people can remember into addresses machines can use.

Run it with:   python3 lookup.py
Or with names: python3 lookup.py wikipedia.org localhost
"""

import socket
import sys

NAMES = ["example.com", "wikipedia.org", "localhost", "no-such-name.example"]


def addresses_for(name):
    """Every address this name resolves to, without duplicates."""
    found = socket.getaddrinfo(name, 80, proto=socket.IPPROTO_TCP)
    return sorted({result[4][0] for result in found})


for name in sys.argv[1:] or NAMES:
    try:
        found = addresses_for(name)
    except socket.gaierror as problem:
        print(f"{name:<22} no answer: {problem.strerror}")
        continue
    print(f"{name:<22} {', '.join(found)}")
