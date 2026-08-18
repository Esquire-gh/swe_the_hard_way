# Chapter 18. AI systems are the same systems

## Is any of this different

The way people write about machine learning suggests a separate discipline. It
has its own vocabulary, its own conferences, its own hardware, and a habit of
describing systems in terms that sound like nothing else in software.

The question for this chapter is narrow. Set aside what a model is and what it
does, which is a different subject and a good one. Ask only about the
engineering. When a model is trained, what is running, and where. When you send
a question to one and words come back, what happened between those two moments.

The answer is that it is this tutorial again. Not similar to it, and not
inspired by it. The same things with different words on them, and this chapter
teaches nothing new on purpose. If it works, the feeling by the end is
recognition rather than learning.

## Training is chapter 1, with the numbers changed

Training a model is a program running on a computer.

There is a file on a disk, or a great many of them, holding the data. A process
is created, in the sense of chapter 1, and the operating system gives it memory
and schedules it. It reads a portion of the data off the disk, does a large
amount of arithmetic, adjusts some numbers it is holding, and does it again.
Millions of times.

The arithmetic runs on a graphics processor rather than the one chapter 1
described, and the difference is one of shape rather than of kind. A GPU has
thousands of simpler processors that all perform the same operation on
different numbers at the same moment, which suits arithmetic on very large
grids of numbers. Chapter 1's fetch, do, advance loop is what each of them is
doing. There are just a lot of them.

Everything else in chapter 1 applies unchanged. The process has a process id.
It can be listed with `ps`. It uses memory that the operating system gave it,
and when it exits that memory is gone, which is why training runs write their
numbers to a disk from time to time. That saved copy is called a
**checkpoint**, and it exists for the reason chapter 15 gave: a process's memory
does not survive the process, and something restarts programs that die, which
is chapter 16's supervisor.

There is a less obvious inheritance from chapter 16. Those thousands of
processors are expensive, and they sit idle if the data does not arrive fast
enough. So a large part of the engineering in training is reading files off
disks quickly and getting them into the right memory, which is the problem of
one slow component holding up everything in front of it.

## Training is also chapter 17

A model too large for one machine, or a training run that would take a year on
one machine, is spread across many. At that point every sentence in chapter 17
applies.

The usual arrangement gives each machine a copy of the numbers and a different
portion of the data. Each does its arithmetic, and then all of them have to
combine their adjustments before the next step, because otherwise they would
drift into being different models.

That combining step is a point where every machine waits for every other one.
Which means the slowest machine sets the pace for all of them, and one machine
that has become slow rather than dead is worse than one that failed, exactly as
chapter 17 described. It also means that a machine failing partway through a
step stops the step, so the run goes back to the last checkpoint and repeats
the work since then.

When the model itself is too large for one machine's memory, it is cut up and
the pieces are placed on different machines, which is chapter 17's partitioning
with the same costs. Work that used to be one operation becomes several
machines exchanging results, and the network between them is the limit rather
than the arithmetic.

None of that is specific to models. It is what happens whenever a computation
is split across machines that have to agree on a shared result at every step.

## A model that answers is chapter 5's server

Training produces a large file of numbers. Using it is a different program with
a completely familiar shape.

A process is started on a machine. It loads that file into memory. It opens a
socket, binds a port, listens, and waits, which is chapters 8 and 9 with no
modification whatsoever. It is a server in exactly chapter 5's sense: it was
running before you arrived, it does not know you exist until you connect, and
it cannot start the conversation.

Your request travels there as chapter 6 described. A request line, headers with
your credentials among them, a blank line, and a body, which for these
particular servers is usually JSON. The answer comes back as a status line,
headers, a blank line and a body. If you have an API key for such a service you
can send that request with `nc` and read the reply, and there is nothing in it
that chapter 6 did not cover.

The **tokens** everybody talks about are one detail worth naming, because the
word is unavoidable. Before the model sees your text it is cut into pieces,
each a common run of characters, and the model works in those pieces rather
than in letters or words. That is a unit of counting. It changes nothing about
the machinery in this chapter.

## Why the words appear one at a time

The one visible difference between a chat window and an ordinary web page is
that the answer arrives gradually. That looks like a new capability and it is
chapter 6.

The file is
[`code/18-ai-systems-are-the-same-systems/stream.py`](../code/18-ai-systems-are-the-same-systems/stream.py).
It is a server that sends a sentence one word at a time, and a client that
prints each piece as it arrives with the time it turned up.

```
$ python3 stream.py
 0.00s  b'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nTransfer-Encoding: chunked\r\n\r\n'
 0.00s  b'2\r\na \r\n'
 0.16s  b'6\r\nmodel \r\n'
 0.31s  b'a\r\nanswering \r\n'
 0.46s  b'3\r\nis \r\n'
 0.62s  b'2\r\na \r\n'
 0.77s  b'7\r\nserver \r\n'
 0.93s  b'8\r\nwriting \r\n'
 1.09s  b'5\r\ntext \r\n'
 1.24s  b'5\r\ndown \r\n'
 1.40s  b'2\r\na \r\n'
 1.56s  b'7\r\nsocket \r\n'
 1.72s  b'0\r\n\r\n'
```

That is `Transfer-Encoding: chunked`, which chapter 6 met on a response from
`example.com` and described as the way a server sends a body whose total length
it does not know when it starts. Each line is a length in hexadecimal, then
that many bytes, then the next one, ending with a length of zero.

A server producing text a piece at a time does not know the total length when
it starts. So it uses the mechanism that already existed for that, and the
words appear as they are produced. Real services usually put a slightly more
structured format inside the same stream, with each piece written as a `data:`
line, but the transport underneath is this.

The connection stays open for the whole answer, which is why chapter 14 and
chapter 17 matter so much for these services. One conversation occupies a slot
for as long as it takes, and how long that is cannot be known in advance.

## Chapter 16, unchanged, with new names

Everything that surrounds one of these servers in production is chapter 16.

Requests arrive faster than the expensive hardware can take them, so they go
into a queue and wait, which is why these services have rate limits and why a
busy one tells you to try again later. That is backpressure, and refusing
quickly is kinder than accepting and never answering.

The hardware is far more efficient doing many requests together than one at a
time, so the server deliberately waits a moment to collect several and runs
them as a group. That is a queue with an intentional delay, trading a little
latency for a lot of throughput, and the version that lets new requests join a
group already in progress is called continuous batching.

While answering, the model reuses results it computed for earlier parts of the
same conversation, and keeping those rather than recomputing them is a cache in
exactly chapter 16's sense. It lives in the expensive memory next to the
processors, which makes it the main limit on how many conversations one machine
can hold at once, and when that memory fills something has to be thrown away.
Cache eviction, with the same trade as always.

When many requests begin with the same long piece of text, the work of
processing that prefix is kept and reused, which is a cache with a key, and the
providers call it prompt caching. The `cf-cache-status: HIT` header from chapter
6 is the same idea at a different layer.

A request that times out may have been completed and billed, so a client that
retries needs chapter 17's identifier to let the server recognise a repeat.
Requests are logged, latency is measured at the ninety fifth and ninety ninth
percentile, and a version that answers only when the model is loaded is a
health check.

## What is genuinely different

Three things, and it is worth being exact about them, because pretending
nothing is different would be as wrong as pretending everything is.

The work per request is enormous and its size cannot be known before it starts.
An ordinary page takes about as long every time. Here the cost depends on how
much text comes back, which is decided while the answer is being produced. That
makes every timeout in chapter 17 and every capacity calculation in chapter 16
harder, because the thing being estimated is genuinely unknown at the moment
you must estimate it.

The same input does not have to produce the same output. A database read is a
function of what is stored. These servers usually choose among possibilities as
they go, so two identical requests can return different text. That does not
break caching, but it means caching is now a decision about behaviour rather
than an optimisation you can apply invisibly.

And the file of numbers is very large. Starting a process means loading tens or
hundreds of gigabytes before it can answer anything, which makes chapter 16's
approach of starting the new version before stopping the old one expensive in a
way it is not for a web application. Deployment strategies for these services
are shaped almost entirely by that one fact.

Notice what is not on that list. Nothing about how the requests arrive, how the
server waits, how the data is stored, how the machines coordinate, or how the
whole thing is deployed and watched.

An agent, while we are here, is a client. It is a program that makes HTTP
requests to a model server, reads the answer, and on the strength of it makes
further HTTP requests to other servers, with retries and timeouts and
idempotency keys. Chapters 5 through 7 describe it completely.

## Check it yourself: read the pieces

Run `stream.py` and look at the fourth line of output.

```
 0.31s  b'a\r\nanswering \r\n'
```

The `a` is a length written in hexadecimal, so it is ten, and `answering ` is
ten bytes including its trailing space. That is the framing chapter 6
described, arriving from a program you wrote, over a socket you opened, three
tenths of a second after the previous piece.

Nothing about that line is about models. It is a length, some bytes, and a line
ending. When you next watch an answer appear a few words at a time in a browser,
that is what is happening underneath, and you have already written both ends of
it.

## What you can now explain

Here is the thing this tutorial set out to make possible. Somebody types an
address, presses enter, and a page appears. This is what happened.

The browser cut the address into a scheme, a host and a path, and asked the
operating system to turn the host into an address. The operating system asked a
resolver, which asked a root server, which knew nothing about the site but knew
who to ask about the last part of the name, and so on down until an address
came back, along with a number of seconds for which the answer may be reused.

The browser asked the operating system for a socket and asked it to connect to
that address on port 443. The operating system, which owns the network card,
made a note in a table, put a packet on the wire, and took the process off the
schedule until an answer came. The packet went to a router in the building,
which read the address, chose a link, and forgot about it, and then to a
handful of machines belonging to companies with no relationship to either end.
Some packets arrived out of order and at least one probably did not arrive at
all, and TCP on the two end machines put them in order and asked again for the
missing one, because the machines in the middle do not know that any of this is
a conversation.

On the far machine a program had been running for weeks, doing nothing. It had
asked the operating system for a socket, bound it to port 443, and called
accept, at which point it was taken off the schedule and used no processor at
all. The arriving connection put it back on. It returned a second socket for
this one conversation and went back to waiting.

The browser wrote a request line, some headers including which site it wanted,
and a blank line. The server read until the blank line, then read exactly as
many further bytes as a header told it to, because the stream underneath has no
message boundaries.

The path did not name a file. It selected a function, which ran, read some rows
out of a program on another machine that speaks its own protocol on its own
port, and built a page. Or it did not run, because an identical answer was
already sitting in a cache somewhere and the site's machines were never
involved. Either way what came back was a status line, some headers, a blank
line, and a body, produced by one of many threads or by one loop holding
thousands of connections, on one of many machines behind a program that holds
the public port so that any of them can be replaced without anybody noticing.

The browser read the response, worked out which of the things it referred to
were parts of the page and which were places you might go, fetched the parts in
parallel, built a tree out of tags according to a specification that also says
exactly how to handle the tags that are wrong, worked out where every box
belongs on a screen the author never saw, and drew it.

If a model was involved, it was a process on a machine, reading numbers it had
saved to a disk, sitting behind a queue and a cache, writing text down a socket
in pieces with a length in front of each one.

There is no layer in that account where the honest answer is that something
happens. You can now name every part of it, and you have written a small
version of most of them.

That was the whole point.

---

[Previous chapter](./17-more-than-one-machine.md) | [Back to the front page](../README.md)
