"""Exercise two: do the browser's first job by hand.

Fetch one document with nc, find every other file it names, decide which
of them are parts of this page and which are places you could go, and
fetch only the parts. That decision is the whole difference between
loading a page and crawling a site.

Start the page first:  python3 -m http.server 8099 -d ../page
Run it with:           python3 fetch_parts.py
"""

import re
import subprocess

HOST, PORT = "localhost", "8099"
START = "/index.html"


def fetch(path):
    """One request, sent through nc, split into headers and body."""
    request = (f"GET {path} HTTP/1.1\r\nHost: {HOST}\r\n"
               f"Connection: close\r\n\r\n")
    raw = subprocess.run(["nc", "-w", "5", HOST, PORT],
                         input=request.encode(), capture_output=True).stdout
    head, _, body = raw.partition(b"\r\n\r\n")
    return head.decode(errors="replace"), body


def named_in(html):
    """Every other file this document names, split by what the name is for."""
    parts = re.findall(r'<(?:img|script)[^>]*\ssrc="([^"]+)"', html)
    parts += re.findall(r'<link[^>]*\shref="([^"]+)"', html)
    destinations = re.findall(r'<a[^>]*\shref="([^"]+)"', html)
    return parts, destinations


head, body = fetch(START)
print(f"{START:<14} {head.splitlines()[0]}   {len(body)} bytes")

parts, destinations = named_in(body.decode())
print(f"\nparts of this page ({len(parts)}):")
for name in parts:
    print(f"    {name}")
print(f"\nplaces you could go ({len(destinations)}), not fetched:")
for name in destinations:
    print(f"    {name}")

print("\nfetching only the parts:")
total = len(body)
for name in parts:
    head, body = fetch("/" + name.lstrip("/"))
    total += len(body)
    print(f"    {name:<14} {head.splitlines()[0]}   {len(body)} bytes")

print(f"\n{1 + len(parts)} requests, {total} bytes, to show one page")
