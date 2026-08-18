"""Take the raw bytes of an HTTP request and pull them apart.

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
    """Split one request into its parts, and whatever came after it."""
    head, _, rest = raw.partition(b"\r\n\r\n")
    lines = head.split(b"\r\n")

    method, path, version = lines[0].split(b" ")
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(b": ")
        headers[name.decode().lower()] = value.decode()

    length = int(headers.get("content-length", 0))
    return method, path, version, headers, rest[:length], rest[length:]


method, path, version, headers, body, leftover = parse(RAW)

print(f"method   {method.decode()}")
print(f"path     {path.decode()}")
print(f"version  {version.decode()}")
print("headers")
for name, value in headers.items():
    print(f"    {name:<16} {value}")
print(f"body     {body!r}")
print(f"\nthe body is {len(body)} bytes, and the header said {headers['content-length']}")
print(f"bytes left over after this message: {len(leftover)}")
