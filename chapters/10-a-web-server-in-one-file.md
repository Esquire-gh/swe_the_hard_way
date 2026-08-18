# Chapter 10. A web server in one file

## Can I really build this myself

Every piece is now on the table. Chapter 8 gave the loop. Chapter 9 gave the
calls that fill the one line the loop could not express. Chapter 6 gave the
text that goes in and comes out, and a parser for it that fitted in thirty
lines.

So the question left over from chapter 9 is whether a person can put those
together and end up with something a real browser will talk to, or whether
there is a further layer of difficulty that has been politely hidden so far.

There is not. The answer is about twenty lines, and the rest of this chapter is
spent making it useful and then finding out what it cannot do.

## The same calls, with Python's names on them

Python's `socket` module is a thin covering over the calls from chapter 9, and
the names line up almost exactly. `socket.socket()` is `socket`. Then `bind`,
`listen` and `accept` are called `bind`, `listen` and `accept`. This is true in
most languages, for the reason chapter 9 gave: they are all asking the same
operating system to do the same thing.

Two names are different and both differences are worth knowing.

Reading is `recv` rather than `read`, and it takes a maximum number of bytes.
What comes back is whatever has arrived so far, up to that maximum, which is
chapter 2's point about a stream having no message boundaries showing up in an
argument list.

Writing is `sendall` rather than `write`. The plain `send` behaves like the
underlying call and may write only part of what you gave it, returning how much
it managed. `sendall` loops until everything has gone. Using `send` and
ignoring the number it returns is a real way to lose the end of a page.

One line in the listings below has no equivalent in chapter 9 and needs a word
now.

```python
listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

When a server stops, the operating system keeps its port reserved for a minute
or two, in case packets from the finished conversations are still in flight.
Without that line, restarting your server during that window fails with
`address already in use`, which you will otherwise meet about four minutes from
now and find baffling.

## A web server in twenty lines

The file is
[`code/10-a-web-server-in-one-file/server_one.py`](../code/10-a-web-server-in-one-file/server_one.py).

```python
import socket

PAGE = b"""<!doctype html>
<html><body>
<h1>Hello from a socket</h1>
<p>This page was written by hand and sent down a file descriptor.</p>
</body></html>
"""

listening = socket.socket()
listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening.bind(("127.0.0.1", 8000))
listening.listen(5)
print("listening on http://127.0.0.1:8000")

while True:
    conversation, who = listening.accept()
    request = conversation.recv(65536)

    print(f"--- {who[0]}:{who[1]} sent {len(request)} bytes ---")
    print(request.decode(errors="replace").rstrip())

    conversation.sendall(
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/html\r\n"
        b"Content-Length: " + str(len(PAGE)).encode() + b"\r\n"
        b"Connection: close\r\n"
        b"\r\n" + PAGE
    )
    conversation.close()
```

Start it, and then in a second window ask it for the page.

```
$ curl -s -D - http://127.0.0.1:8000/
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 143
Connection: close

<!doctype html>
<html><body>
<h1>Hello from a socket</h1>
<p>This page was written by hand and sent down a file descriptor.</p>
</body></html>
```

Open `http://127.0.0.1:8000` in an actual browser and the heading appears, in
whatever a heading looks like on your machine, from a response you assembled
out of byte strings.

The address is `127.0.0.1`, which chapter 4 introduced as the name a machine
has for itself. Nothing here leaves the laptop, and nobody else on the internet
can reach it, for the reason chapter 4 gave about private addresses. Making it
public is a separate job and it belongs to chapter 16.

## What the browser sent

The server prints what arrives, so the first window now holds the other side of
chapter 6.

```
listening on http://127.0.0.1:8000
--- 127.0.0.1:59470 sent 77 bytes ---
GET / HTTP/1.1
Host: 127.0.0.1:8000
User-Agent: curl/8.2.1
Accept: */*
```

That is chapter 7's hand typed request, arriving from the other direction. The
port on the visitor's end, 59470, is the fourth number from chapter 9, picked by
the operating system out of whatever was free.

Try it with a browser instead and you will get a longer list of headers, and
usually a second request for `/favicon.ico` a moment later, which your server
happily answers with the same page. Nothing about the protocol stops a server
returning a page where an icon was asked for. Being correct is your job.

## Serving files off the disk

A server that returns one hard coded page is not much of a claim. The change
that makes it a web server is to take the path out of the request line and read
the matching file off the disk, which is exactly what chapter 4 said a website
was.

There is a small site to serve in
[`code/10-a-web-server-in-one-file/site/`](../code/10-a-web-server-in-one-file/site/),
holding two pages and a stylesheet.

The file is
[`code/10-a-web-server-in-one-file/server_files.py`](../code/10-a-web-server-in-one-file/server_files.py),
and it contains a bug on purpose. The next section is about the bug.

```python
import pathlib
import socket

ROOT = pathlib.Path(__file__).parent / "site"
TYPES = {".html": "text/html", ".css": "text/css", ".txt": "text/plain"}


def response(status, kind, body):
    """One HTTP response, headers and all, as bytes."""
    head = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {kind}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode() + body


def answer(path):
    wanted = ROOT / path.lstrip("/")
    if wanted.is_dir():
        wanted = wanted / "index.html"
    if not wanted.is_file():
        return response("404 Not Found", "text/html", b"<h1>404 not found</h1>")
    kind = TYPES.get(wanted.suffix, "application/octet-stream")
    return response("200 OK", kind, wanted.read_bytes())


listening = socket.socket()
listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening.bind(("127.0.0.1", 8000))
listening.listen(5)
print(f"serving {ROOT.name}/ on http://127.0.0.1:8000")

while True:
    conversation, _ = listening.accept()
    request = conversation.recv(65536)
    path = request.split(b" ")[1].decode() if request.count(b" ") >= 2 else "/"
    print(f"asked for {path}")
    conversation.sendall(answer(path))
    conversation.close()
```

Point a browser at it and the site works. Following the link to the second page
works. The stylesheet arrives and the page is laid out. The server's own window
shows why:

```
serving site/ on http://127.0.0.1:8000
asked for /
asked for /style.css
asked for /missing.html
```

Three separate requests, three separate connections, three separate trips
through `accept`. This is chapter 7's observation seen from the far side. The
browser asked for the page, read it, found it referred to a stylesheet, and
came back for that. Your twenty lines did not have to know anything about
stylesheets to serve one, because `Content-Type` is a label and the browser
does the rest.

The third line is a request for a file that does not exist, and the server
answered `404`. Chapter 3's decision, chapter 6's number, your code.

## The bug you just wrote

Now the part that makes this a chapter about writing servers rather than a
chapter about sockets.

`ROOT / path.lstrip("/")` joins whatever the visitor typed onto the end of your
directory. Visitors are strangers, and one of the things a stranger can type is
`..`.

Next to the server, outside `site/`, there is a file called
`not-for-the-public.txt`. A browser will not send this request, because
browsers tidy up paths before sending them. Chapter 7 showed that you do not
need a browser.

```
$ printf 'GET /../not-for-the-public.txt HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n' \
    | nc 127.0.0.1 8000
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 121
Connection: close

This file sits next to the server, outside the site/ directory.
Nobody visiting the site should ever be able to read it.
```

Enough `../` and the same request reads any file the server process has
permission to open, anywhere on the machine. This has a name, **path
traversal**, and it is one of the oldest mistakes in web software. It is worth
seeing on your own server, in a file you wrote, because the line that causes it
looks completely reasonable.

The fix is to work out the real location the path resolves to, and refuse
anything that is not inside the directory you meant to serve.

```python
def answer(path):
    wanted = (ROOT / path.lstrip("/")).resolve()
    if ROOT.resolve() not in wanted.parents and wanted != ROOT.resolve():
        return response("403 Forbidden", "text/html", b"<h1>403 forbidden</h1>")
    ...
```

`resolve` follows the `..` parts and any shortcuts on the disk and reports where
the path genuinely lands. Then the check is whether the directory you are
serving is one of its parents. The corrected server is
[`code/10-a-web-server-in-one-file/server_safe.py`](../code/10-a-web-server-in-one-file/server_safe.py),
and the same request against it gets nothing.

```
$ printf 'GET /../not-for-the-public.txt HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n' \
    | nc 127.0.0.1 8000
HTTP/1.1 403 Forbidden
Content-Type: text/html
Content-Length: 22
Connection: close

<h1>403 forbidden</h1>
```

Keep the shape of that reasoning, because it recurs for the rest of this
tutorial. Everything arriving from outside is text a stranger chose, and every
place your code uses it to reach something is a place where the stranger is
choosing what you reach.

## Check it yourself: ask for a file the server cannot type

Run `server_safe.py`, and ask it for something that does not exist.

```
$ curl -s -o /dev/null -w "status for a missing file: %{http_code}\n" \
    http://127.0.0.1:8000/missing.html
status for a missing file: 404
```

Then add a file to `site/` while the server is running, without restarting it,
and ask for that. It works. The server holds no list of pages, has no idea what
is in the directory, and finds out what exists at the moment somebody asks.

That is worth a moment because it is the definition of the thing being served.
There is no website inside your program. There is a directory, and a program
that will read out of it when asked.

## Where this falls apart

You have a web server, and this is where its limits should be stated plainly,
because the next chapters are each named after one of them.

It answers one visitor at a time. The loop accepts a conversation, deals with
it from start to finish, and only then goes back to `accept`. A second visitor
waits in the queue that `listen(5)` created. With small local files nobody
notices. Make one request slow and everybody behind it stops, and that is
chapter 14.

It can only send back files that already exist. Every visitor gets identical
bytes. Nothing on the page can be different for one person, which rules out
logging in, writing anything, or knowing that a visitor was here before, and
that is chapter 12.

It forgets everything. When you press control C, everything the program knew is
gone, because it was in memory belonging to a process, as chapter 1 described.
That is chapter 15.

It reads one buffer of 65,536 bytes and hopes the whole request arrived. Chapter
6 was explicit that a stream has no message boundaries, and this code ignores
that, so a request split across two packets will be handled wrongly.

None of that makes it a toy. Every one of those limits was a limit real servers
had, and the order in which they were fixed is roughly the order of the rest of
this tutorial.

Before any of it, there is a smaller thing to sort out. You have now written a
server, and you are sitting at a laptop. There is a word being used for two
different objects, and the confusion it causes is out of proportion to how long
it takes to clear up.

---

[Previous chapter](./09-what-a-socket-is.md) | [Next chapter](./11-server-as-hardware-server-as-software.md)
