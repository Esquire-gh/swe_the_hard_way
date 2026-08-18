# Chapter 7. Why we need browsers

## Three jobs, and nothing yet doing them

Chapter 6 finished with three things that have to happen and nothing doing any
of them. The request has to be sent. The response has to be turned into
something a person can look at. And somebody, somewhere, has to have decided
what `<h1>` means, or the whole arrangement is two programs exchanging
punctuation.

One kind of program does all three, and we call it a browser. That is a large
piece of software, larger than most operating systems were when the web was
invented, so it is fair to ask what all of it is for.

The best way to find out is to do the jobs yourself and see which ones you can
finish. The first one takes a single line.

## A program that joins two points and stays out of the way

To send the text from chapter 6 you need something that will open a connection
to another machine and then get out of the way. `nc`, short for netcat, is
that. It connects, copies whatever you give it into the connection, and prints
whatever comes back. It knows nothing about HTTP and has no opinion about what
you send. It is a pipe with a network on one end.

It needs two things: which machine, and which of the waiting programs on that
machine you want.

That second one has been in the background since chapter 5 and is worth naming
now. A machine runs many waiting programs at once, which you saw in the `LISTEN`
listing, so an address on its own is not enough to say who you mean. Every
waiting program claims a number, and every packet carries the number it is for.
The number is called a **port**, and it is what the operating system uses to
decide which waiting program a new connection belongs to. Chapter 9 is about
the mechanism. For now, the web agreed long ago that plain HTTP lives on port
80 and encrypted HTTP on port 443, which is why you have never had to type
either.

## Sending a request by hand

The target here is `info.cern.ch`, which is the machine CERN keeps at the
address of the first website. It still answers unencrypted HTTP on port 80,
which most large sites no longer do, so it is a good place to watch the plain
protocol work.

```
$ printf 'GET / HTTP/1.1\r\nHost: info.cern.ch\r\nConnection: close\r\n\r\n' \
    | nc info.cern.ch 80
```

Three details in that command matter. `printf` is used rather than `echo`
because chapter 6 said every line ends with a carriage return and a line feed,
and `printf` writes those two bytes exactly where they are asked for.
`Connection: close` asks the server to hang up once it has answered, since
HTTP/1.1 otherwise keeps the connection open for a further request and `nc`
would sit there waiting. And the request ends with two line endings in a row,
which is the blank line that ends the headers.

Here is the whole of what came back.

```
HTTP/1.1 200 OK
Date: Tue, 18 Aug 2026 04:48:30 GMT
Server: Apache
Last-Modified: Wed, 05 Feb 2014 16:00:31 GMT
ETag: "286-4f1aadb3105c0"
Accept-Ranges: bytes
Content-Length: 646
Connection: close
Content-Type: text/html

<html><head></head><body><header>
<title>http://info.cern.ch</title>
</header>

<h1>http://info.cern.ch - home of the first website</h1>
<p>From here you can:</p>
<ul>
<li><a href="http://info.cern.ch/hypertext/WWW/TheProject.html">Browse the first website</a></li>
<li><a href="http://line-mode.cern.ch/www/hypertext/WWW/TheProject.html">Browse the first website using the line-mode browser simulator</a></li>
<li><a href="http://home.web.cern.ch/topics/birth-web">Learn about the birth of the web</a></li>
<li><a href="http://home.web.cern.ch/about">Learn about CERN, the physics laboratory where the web was born</a></li>
</ul>
</body></html>
```

Everything chapter 6 described is there and nothing else is. A status line.
Eight headers. A blank line. Then exactly 646 bytes of HTML, the number the
`Content-Length` header promised. `Last-Modified` says the file on that disk was
written in February 2014 and has not been touched since, which is the clearest
possible statement of what a web page is.

That is the first job done, in one line, with no browser anywhere. Sending an
HTTP request is not what browsers are for.

## What you did not get

Two things are missing, and one of them is worse than it looks.

The obvious one is that you have angle brackets rather than a page. Turning
those into something readable means building a tree out of the nested tags,
deciding what every element should look like, working out the position and size
of every box on a screen whose width was not known when the document was
written, drawing all of it, and doing the whole calculation again when anything
changes. That is a real engineering problem and it is most of what a browser's
code is.

The less obvious one is that a page is rarely one file. The CERN page above is
unusual because it is genuinely self contained. A more typical page is not.
Fetching the front page of Wikipedia gives 120,361 bytes of HTML that refer to
three files with `src`, which the browser must fetch to display the page at
all, and five more named by `<link>` tags, which are its stylesheet and its
icons. It also contains 376 links you could follow, which the browser must not
fetch, because those are places you might choose to go rather than parts of
this page.

So a browser reads the document, works out which of those references are parts
of the page and which are destinations, opens several connections at once,
often to different machines, fetches the parts, and assembles the result while
it is still arriving. Doing that by hand with `nc` is possible. It is eight
more commands for that one page, and you have to read the HTML yourself to know
what the eight are.

## Who decided what the tags mean

The third job is not engineering, and it is the one that made browsers into
what they are.

In 1991 HTML was about twenty tags and there was no committee. Then in 1993 the
NCSA at the University of Illinois released Mosaic, the first browser most
people ever saw, and Marc Andreessen proposed a tag for putting a picture in a
page. `<img>` was not standardised, agreed, or approved. It was implemented,
it was useful, and it stayed.

That set the pattern. Netscape Navigator arrived in 1994 and Microsoft's
Internet Explorer in 1995, and for the next six years the two competed by
inventing tags. Pages began carrying badges saying which browser they required.
The idea from chapter 3, that a document should be readable on any machine
because it describes itself rather than the screen, was quietly dying.

Berners-Lee founded the World Wide Web Consortium in 1994 to write down what
HTML actually meant. It published HTML 2.0 in 1995, 3.2 in 1997, and 4.01 in
1999. Then it went after a stricter successor, XHTML, which required documents
to be well formed and would refuse to display them otherwise. The web that
existed was not well formed and never would be, so the browsers did not follow.

In 2004 people from Mozilla, Opera and Apple formed a separate group, the
WHATWG, to carry on developing HTML in a way that stayed compatible with what
was already published. That work became HTML5. In 2019 the two bodies agreed
there would be one version and it would be the WHATWG's.

Out of all of that, one detail explains why browsers are the size they are.

The modern HTML specification does not only define what correct HTML means. It
defines, step by step, what a browser must do with incorrect HTML. Tags that
are never closed, tags closed in the wrong order, text in places no text is
allowed. For each case the specification says exactly which elements to create
and where to put them, so that every browser given the same broken document
builds precisely the same tree.

That exists because a large part of the web is malformed and cannot be
repaired. Nobody can edit the pages, and many of their authors are dead. So the
standard gave up on requiring correctness and required identical handling of
incorrectness instead.

This is the third job, and it is why writing a browser is hard. Speaking the
protocol is thirty lines, as chapter 6 showed. Drawing a page is a serious
piece of engineering. Agreeing with every other browser about what a broken
document means is neither, and it is the largest of the three.

## Check it yourself: leave one header out

Send the same request with the `Host` line removed.

```
$ printf 'GET / HTTP/1.1\r\nConnection: close\r\n\r\n' | nc info.cern.ch 80
HTTP/1.1 400 Bad Request
Date: Tue, 18 Aug 2026 04:48:39 GMT
Server: Apache
Content-Length: 226
Connection: close
Content-Type: text/html; charset=iso-8859-1
```

HTTP/1.1 requires that header, for the reason chapter 6 gave, and the server
refused the request rather than guessing. Then ask for something that is not
there.

```
$ printf 'GET /nothing-here HTTP/1.1\r\nHost: info.cern.ch\r\nConnection: close\r\n\r\n' \
    | nc info.cern.ch 80
HTTP/1.1 404 Not Found
Date: Tue, 18 Aug 2026 04:48:31 GMT
Server: Apache
Content-Length: 196
Connection: close
Content-Type: text/html; charset=iso-8859-1
```

There is chapter 3's decision, arriving as a number, from a real server, in
response to a request you typed yourself.

The thing to take from both is what did not happen. You have used a browser
thousands of times and it has never once let you send a request without a
`Host` header, or with the line endings wrong, or with the blank line missing.
Getting the request exactly right, every time, against servers written across
thirty years, is a job you have been handing to someone else without noticing.

All three requests are in
[`code/07-why-we-need-browsers/by_hand.sh`](../code/07-why-we-need-browsers/by_hand.sh)
if you would rather run them together.

## Now look at the side that answers

Everything from chapter 4 to here has been about the side that asks. How it
turns a name into an address, what it sends, what comes back, and what it has
to do afterwards.

In every one of those experiments there was a program on the other end that was
already running. It had been started long before, it was waiting on port 80, it
accepted the connection, read the text, found a file, and wrote text back. We
have treated it as scenery.

It is not scenery. It is the thing this tutorial is about, and it is smaller
than the browser by a very long way. The rest of part four builds it, and by
chapter 10 you will have written one that a browser will talk to.

The first question is the one chapter 5 raised and left alone. A server spends
almost all of its life waiting for somebody to arrive. What does waiting
actually mean, for a program.

---

[Previous chapter](./06-requests-and-responses-are-just-text.md) | [Next chapter](./08-how-a-server-receives-a-request.md)
