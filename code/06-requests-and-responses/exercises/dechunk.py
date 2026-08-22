"""Exercise two: read a body whose length nobody knew in advance.

When a server starts sending before it knows how much there will be, it
cannot write a Content-Length. Instead it sends the body in pieces, each
one preceded by its length in hexadecimal, and ends with a piece of length
zero. This is what curl --raw showed against example.com.

Run it with: python3 dechunk.py
"""

CHUNKED = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/plain\r\n"
    b"Transfer-Encoding: chunked\r\n"
    b"\r\n"
    b"17\r\nthe first piece of body\r\n"
    b"c\r\nand the rest\r\n"
    b"0\r\n\r\n"
)


def dechunk(rest):
    """Join the pieces of a chunked body, and return whatever came after."""
    body = b""
    while True:
        line, _, rest = rest.partition(b"\r\n")
        size = int(line.split(b";")[0], 16)      # hexadecimal, options ignored
        if size == 0:
            return body, rest.partition(b"\r\n")[2]
        body += rest[:size]
        rest = rest[size + 2:]                   # step over the piece's own \r\n


head, _, rest = CHUNKED.partition(b"\r\n\r\n")
body, leftover = dechunk(rest)

print("the pieces as they arrived:")
print(f"    {rest!r}")
print(f"\nthe body, joined:  {body!r}")
print(f"bytes it turned out to be: {len(body)}")
print(f"left over after the message: {len(leftover)}")
