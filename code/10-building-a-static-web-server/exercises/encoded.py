"""Exercise one: why the fix has to check the destination, not the text.

Three guards, four requests. Two of the guards look at the path a stranger
sent and try to spot something bad in it. The third works out where the
path really lands and asks whether that is inside the folder being served.
Only one of the three is still standing at the end.

Run it with: python3 encoded.py
"""

import pathlib
from urllib.parse import unquote

ROOT = (pathlib.Path(__file__).parent.parent / "site").resolve()
PRIVATE = "not-for-the-public.txt"

REQUESTS = [
    "/about.html",
    "/../" + PRIVATE,
    "/%2e%2e%2f" + PRIVATE,           # .. and / written as percent escapes
    "/..%2f" + PRIVATE,               # only the slash escaped
]


def spot_dots(path):
    """Refuse anything with .. in it. Then decode, as paths arrive encoded."""
    if ".." in path:
        return "403 refused"
    return open_it(unquote(path))      # the decoding happens after the check


def spot_dots_first(path):
    """The same guard, with the decoding moved in front of it."""
    path = unquote(path)
    if ".." in path:
        return "403 refused"
    return open_it(path)


def check_destination(path):
    """Work out where it lands, and refuse anything outside ROOT."""
    wanted = (ROOT / unquote(path).lstrip("/")).resolve()
    if ROOT not in wanted.parents and wanted != ROOT:
        return "403 refused"
    return open_it(unquote(path))


def open_it(path):
    wanted = (ROOT / path.lstrip("/")).resolve()
    if wanted.is_file():
        return "200 sent " + wanted.name
    return "404 not found"


GUARDS = [("looks for .., then decodes", spot_dots),
          ("decodes, then looks for ..", spot_dots_first),
          ("checks where it lands", check_destination)]

for name, guard in GUARDS:
    print(f"a guard that {name}:")
    for request in REQUESTS:
        print(f"    {request:<34}{guard(request)}")
    print()
