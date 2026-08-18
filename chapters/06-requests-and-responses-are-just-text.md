# Chapter 6. Requests and responses are just text

## What the two programs actually say

Chapter 5 left a client and a server facing each other with nothing agreed
between them. The client was written by one group of people and the server by
another, years apart, in different languages, and neither has ever heard of the
other. A browser released this month has to be able to ask a server that has
not been touched since 2009 for a page and understand what comes back.

The only way that works is if both were built against the same written
agreement. This chapter is that agreement, and the surprise is how little of it
there is. What travels between a browser and a server is text, in lines, and
you can read all of it.

## An agreement designed to be read by people

The rules are called the **Hypertext Transfer Protocol**, or HTTP.

The first version, in 1991, was one line long. The client sent `GET` and a
path, the server sent the document back and closed the connection, and that was
the entire protocol. There were no headers, no status codes, and no way to send
anything other than a document. Every piece that came later was added because
something specific did not work, which is the only reason to keep the history
in mind.

A request today looks like this.

```
GET /about.html HTTP/1.1
Host: example.com
User-Agent: curl/8.2.1
Accept: */*

```

The first line is the **request line**, and it has three parts separated by
single spaces. The **method** says what you want done. `GET` means send me
this, and `POST` means here is some data, do something with it. The **path** is
the last part of the URL from chapter 4. The **version** tells the server which
set of rules the client is speaking.

Everything after that until the blank line is a **header**, one per line,
written as a name, a colon, and a value. Headers are notes about the message
rather than the message itself.

One of them deserves attention now, because it explains something chapter 4
left hanging. The path in the request line does not say which site you want,
only which file. `Host: example.com` is what says which site. That header
exists because one machine at one address serves many different sites, and the
machine has no way of knowing which name you typed unless you tell it. In 1991
there was one site per machine and no such header. It became mandatory in
HTTP/1.1 in 1997, and it is what makes shared hosting possible.

Then a blank line, and then optionally a body. A `GET` has no body, because
there is nothing to send. A `POST` does.

A response has the same shape with a different first line.

```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 559

<!doctype html>...
```

The **status line** carries the version, a three digit code, and a short phrase.
The code is for the program and the phrase is for the person reading over its
shoulder. The first digit is the whole classification. Two hundreds mean it
worked. Three hundreds mean the thing is somewhere else and here is where.
Four hundreds mean the client asked for something wrong. Five hundreds mean the
server broke while trying.

`404` is a four hundred, and it is worth pausing on. It is the number the web
gave to chapter 3's decision that links are allowed to break. The server is not
malfunctioning when it sends one. It is reporting, in the ordinary course of
business, that the thing you named is not here, and both programs carry on
afterwards.

## Where a message ends, and why that is the hard part

There is one structural problem underneath all of this, and it comes straight
from chapter 2.

TCP delivers an ordered stream of bytes. It does not deliver messages. Nothing
in it marks where one thing stops and the next begins, because it has no idea
that the bytes mean anything at all. When a program reads from a connection it
gets whatever has arrived so far, which might be half a request, or one request
and the first forty bytes of the next.

So every protocol built on top of TCP has to mark its own boundaries, and HTTP
does it in two places.

The blank line ends the headers. That is the entire job of the blank line, and
it is why it is not optional and not decoration. A reader consumes lines until
it meets an empty one, and then it knows the headers are complete.

The length of the body is stated in the headers. Usually that is
`Content-Length`, giving the exact number of bytes to read. Sometimes the
server does not know the total when it starts sending, so it uses
`Transfer-Encoding: chunked` instead and sends the body in pieces, each piece
preceded by its own length, ending with a piece of length zero.

Forgetting this is the most common way a hand written server breaks, and the
server in chapter 10 will get it wrong before it gets it right.

## A real exchange, read line by line

`curl` is a program that speaks HTTP from a command line, and asking it to be
verbose makes it print both sides of the conversation. Lines beginning `>` are
what it sent. Lines beginning `<` are what came back.

```
$ curl -sv --http1.1 -o /dev/null http://example.com/
> GET / HTTP/1.1
> Host: example.com
> User-Agent: curl/8.2.1
> Accept: */*
>
< HTTP/1.1 200 OK
< Date: Tue, 18 Aug 2026 04:40:50 GMT
< Content-Type: text/html
< Transfer-Encoding: chunked
< Connection: keep-alive
< Server: cloudflare
< Last-Modified: Wed, 12 Aug 2026 20:17:18 GMT
< Allow: GET, HEAD
< Accept-Ranges: bytes
< Age: 14284
< cf-cache-status: HIT
< CF-RAY: a2ce3e22697b3788-EWR
<
```

Four things in there are worth reading properly.

The request is four lines and a blank one. That is the whole of what a client
must send to fetch a page, and you could type it yourself, which is what
chapter 7 does.

This response uses `Transfer-Encoding: chunked` rather than `Content-Length`.
Both are the same idea from the previous section, solving it for different
situations.

`Server: cloudflare` means the machine that answered is not the machine that
owns the site. Something in the middle handled this without the site's own
computers being involved at all. That is chapter 16 and chapter 17 arriving
early, and it is worth noticing that it is visible from here.

`Age: 14284` says this answer had been sitting in a store for about four hours
before it was handed to me, and `cf-cache-status: HIT` says the same thing in
different words. Nobody read a file off a disk to answer this request. Chapter
16 is about why that became necessary.

## The document that came back

Ask for the body rather than throwing it away and you get 559 bytes:

```
$ curl -s --http1.1 http://example.com/
<!doctype html><html lang="en"><head><title>Example Domain</title><link rel="icon" href="data:,"><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{background:#eee;width:60vw;margin:15vh auto;font-family:system-ui,sans-serif}h1{font-size:1.5em}div{opacity:0.8}a:link,a:visited{color:#348}</style></head><body><div><h1>Example Domain</h1><p>This domain is for use in documentation examples without needing permission. Avoid use in operations.</p><p><a href="https://iana.org/domains/example">Learn more</a></p></div></body></html>
```

This is **HTML**, and the first thing to be exact about is that it is a
different agreement from HTTP. HTTP is the envelope, and it does not care what
is inside. HTML is one of the things you can put in the envelope, and the
`Content-Type: text/html` header is the label on the outside saying which.
Images, video, and machine readable data travel in identical envelopes with
different labels.

The whole page is one line, because the spaces between tags carry no meaning
and somebody removed them to save bytes.

What HTML does is mark up structure. `<h1>Example Domain</h1>` says that the
text between those marks is a top level heading. It does not say what a heading
looks like. That is chapter 3's fourth decision, the one about describing the
document rather than the screen, written down as a format. A phone, a laptop
and a program that reads pages aloud to somebody who cannot see them all
receive the same bytes and each decides what a heading should be.

The tags nest, and the nesting is the structure. The `<a href="...">` is a
link, and it is the thing from chapter 3 made real. It points one way, nobody
checked that it works, and the page is perfectly valid if it is broken.

The part in `<style>` is CSS, a third agreement, which is about appearance.
This tutorial does not cover it. It is worth knowing what it is so you can tell
which of the three you are looking at.

## Thirty lines that understand a request

Since a request is text in a fixed shape, a program that understands one is
short. The file is
[`code/06-requests-and-responses-are-just-text/parse.py`](../code/06-requests-and-responses-are-just-text/parse.py).

```python
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
```

Running it:

```
$ python3 parse.py
method   POST
path     /search
version  HTTP/1.1
headers
    host             example.com
    user-agent       curl/8.7.1
    content-type     application/x-www-form-urlencoded
    content-length   11
body     b'q=packets\r\n'

the body is 11 bytes, and the header said 11
bytes left over after this message: 0
```

Notice the lines that are doing the work. `partition` on a blank line separates
the headers from everything else. Splitting the first line on spaces gives
three fields. Splitting each header on the first colon gives a name and a
value. Reading exactly `Content-Length` bytes gives the body. That is the
protocol.

This is a small version of a real thing rather than a pretend one. A parser
used in production adds limits on how long a header may be, careful handling of
input designed to break it, support for chunked bodies, and a great deal of
attention to what to do when the text is malformed. What it does not add is a
different shape.

## Check it yourself: two messages in one stream

The claim worth testing is the one about boundaries, because it is the one that
sounds like a detail.

Change the last part of the file to read `parse(RAW + RAW)` instead of
`parse(RAW)`, which puts two complete requests back to back in one run of
bytes, exactly as they would arrive on a busy connection. Run it again.

```
body     b'q=packets\r\n'

the body is 11 bytes, and the header said 11
bytes left over after this message: 148
```

The parsed message is identical. Nothing about the first request changed just
because a second one was stuck to the end of it, and the parser stopped in the
right place with 148 bytes remaining, which is the second request untouched and
waiting.

Now consider what the parser had to go on. There is no marker in those bytes
saying that the first message ended. No blank line separates the two, and the
second request starts immediately after the last byte of the first body. The
only reason the boundary was found is that a header stated a number and the
parser believed it.

Throw those leftover bytes away and the second visitor is silently ignored.
Read too far and you consume the beginning of somebody else's request and both
break. Both of these are real bugs that real servers have shipped, and you now
know what causes them.

## What still has to happen

We can write a request by hand and we can read a response. What we cannot yet
do is anything at all.

Text does not send itself. Something has to open a connection to the right
machine, write those exact bytes into it, and read the answer back out. Nothing
so far in this tutorial has done that, and chapters 8 and 9 are about the
machinery underneath it.

Then there is the other half. Even with the response in hand, we have 559 bytes
of angle brackets. Something has to turn `<h1>` into a large line of text on a
screen. And that raises a question the format cannot answer for itself. Who
decided that `<h1>` means a heading. HTML is only useful if the program reading
it agrees with the program that wrote it, and there is no authority in the
bytes to enforce it.

Sending the text, drawing the result, and agreeing on what the marks mean are
three jobs. One kind of program does all three, and how it came to be trusted
with the third one is a stranger story than the other two.

---

[Previous chapter](./05-the-client-server-model.md) | [Next chapter](./07-why-we-need-browsers.md)
