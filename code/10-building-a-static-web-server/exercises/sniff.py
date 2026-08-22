"""Exercise two: decide Content-Type from the bytes, not from the name.

server_files.py reads the label off the end of the filename, which is a
guess that the person who named the file was telling the truth. Most file
formats begin with a few fixed bytes that say what they are. This builds
both tables and runs them over a folder where one file is lying.

Run it with: python3 sniff.py
"""

import pathlib

BY_SUFFIX = {".html": "text/html", ".css": "text/css", ".txt": "text/plain",
             ".png": "image/png", ".gif": "image/gif", ".jpg": "image/jpeg"}

BY_FIRST_BYTES = [
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"GIF89a", "image/gif"),
    (b"GIF87a", "image/gif"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"%PDF-", "application/pdf"),
]

MARKUP = (b"<!doctype html", b"<html")

SAMPLES = pathlib.Path(__file__).parent / "samples"
SAMPLES.mkdir(exist_ok=True)
(SAMPLES / "page.html").write_bytes(b"<!doctype html>\n<h1>a page</h1>\n")
(SAMPLES / "look.css").write_bytes(b"body { color: #222 }\n")
(SAMPLES / "dot.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 24)
(SAMPLES / "square.gif").write_bytes(b"GIF89a" + b"\x00" * 24)
(SAMPLES / "trust-me.html").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 24)


def by_suffix(path):
    return BY_SUFFIX.get(path.suffix, "application/octet-stream")


def by_first_bytes(path):
    start = path.read_bytes()[:16]
    for signature, kind in BY_FIRST_BYTES:
        if start.startswith(signature):
            return kind
    if start.lower().startswith(MARKUP):
        return "text/html"
    return "text/plain" if start.isascii() else "application/octet-stream"


print(f"{'file':<16}{'from the name':<26}{'from the bytes':<26}")
for path in sorted(SAMPLES.iterdir()):
    named, sniffed = by_suffix(path), by_first_bytes(path)
    flag = "   <- these disagree" if named != sniffed else ""
    print(f"{path.name:<16}{named:<26}{sniffed:<26}{flag}")

for leftover in SAMPLES.iterdir():
    leftover.unlink()
SAMPLES.rmdir()
