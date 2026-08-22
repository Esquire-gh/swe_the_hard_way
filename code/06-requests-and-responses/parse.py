"""Take the raw bytes of an HTTP message and pull them apart.

Both halves of the conversation have the same shape, so one function reads
both: a first line of three fields, headers, a blank line, and a body whose
length the headers state.

Run it with: python3 parse.py
"""

RAW = (
    b"POST /search HTTP/1.1\r\n"
    b"Host: example.com\r\n"
    b"User-Agent: curl/8.7.1\r\n"
    b"Content-Type: application/x-www-form-urlencoded\r\n"
    b"Content-Length: 11\r\n"
    b"\r\n"
    b"q=packets\r\n"
)


def parse(raw):
    """Split one message into its parts, and whatever came after it."""
    head, _, rest = raw.partition(b"\r\n\r\n")
    lines = head.split(b"\r\n")

    first = lines[0].split(b" ", 2)
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(b": ")
        headers[name.decode().lower()] = value.decode()

    length = int(headers.get("content-length", 0))
    return first, headers, rest[:length], rest[length:]


def response(status, body, kind="text/html"):
    """One HTTP response, headers and all, as bytes."""
    head = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {kind}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode() + body


def show(label, raw):
    first, headers, body, leftover = parse(raw)
    print(label)
    print(f"    {'first line':<16} {' | '.join(part.decode() for part in first)}")
    for name, value in headers.items():
        print(f"    {name:<16} {value}")
    print(f"    {'body':<16} {body!r}")
    print(f"    {'left over':<16} {len(leftover)} bytes")


if __name__ == "__main__":
    show("the request, parsed:", RAW)

    answer = response("404 Not Found", b"no document with that name\n", "text/plain")
    print("\nthe response we built, one line at a time:")
    head, _, sent = answer.partition(b"\r\n\r\n")
    for line in head.split(b"\r\n"):
        print("    " + repr(line + b"\r\n"))
    print("    " + repr(b"\r\n") + "        <- ends the headers")
    print("    " + repr(sent))

    print()
    show("the same function reading it back:", answer)
