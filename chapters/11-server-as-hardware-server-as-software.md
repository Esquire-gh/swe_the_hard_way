# Chapter 11. Server as hardware, server as software

## You wrote a server, and you are sitting at a laptop

Chapter 10 finished with a working web server, running on whatever machine you
are reading this on. Which raises a small question that turns out to be worth
five minutes.

Is your laptop a server now.

It is answering HTTP requests, which is the whole job description from chapter
5. But nobody would call it a server, and if you told a colleague that your
server was a laptop with 40 browser tabs open they would ask you what you
meant. The word is doing two jobs, and mixing them up makes a lot of writing on
this subject harder to read than it needs to be.

## The two things the word means

A **server** in the sense chapter 5 defined is a program. It waits, it accepts
connections, it answers, and it goes back to waiting. That is a role a process
plays, and any machine can run one. `server_safe.py` is a server in this sense.

A **server** in the other sense is a physical computer, and specifically one
built for running programs like that continuously. It usually has no screen or
keyboard, it is shaped to slide into a rack, it has more memory and more
processors than a desktop, often two power supplies in case one fails, memory
that can detect and correct its own errors, and some way to be restarted by
somebody who is not in the building.

The two meanings share a word for a boring historical reason. For a long time,
if you were running server programs, you bought a machine specifically to do
it, and nothing else ran on that machine. Naming the box after its job was
reasonable, because the box had one job.

## Why keeping them apart matters now

That one to one relationship is gone in both directions, and both directions
are worth seeing.

One machine runs many servers. Chapter 5 had you list the programs on your own
laptop in the waiting state, and there were more than you expected. Here is
that list again while chapter 10's server is running:

```
$ lsof -nP -iTCP -sTCP:LISTEN
COMMAND     PID    NAME
com.docke   52512  *:8000 (LISTEN)
python3.1   77974  127.0.0.1:8000 (LISTEN)
```

Two programs, one machine, and the machine is a laptop. The operating system's
list does not distinguish your twenty lines from anything else on it, because
there is nothing to distinguish.

One server runs on many machines. The thing people call "the Wikipedia server"
is a large number of computers in several countries, and chapter 4 already
showed you one name resolving to several addresses. Chapter 17 is about what
that costs.

And the machine may not be a machine. When you rent a server today you are
usually given a **virtual machine**, which is a computer implemented in
software on top of a real one, convinced it has hardware of its own. One
physical box runs several of them, belonging to different customers who have
never met. A **container** is a lighter arrangement again, and it is not a
machine at all: it is ordinary processes on the host, as described in chapter 1,
given a restricted view of the filesystem and the network so they behave as
though they were alone. Chapter 16 is where those earn their place, so this is
only enough to stop the words being frightening.

The practical value of separating the two meanings shows up when something
breaks. "The server is down" can mean the building lost power, or that the
machine is fine and your process exited four minutes ago. Those have nothing in
common except the sentence.

## The other split: web server and application server

There is a second overloading inside the software meaning, and chapter 12 is
about to walk straight into it.

Your `server_safe.py` reads files off a disk and sends them back. A program
whose job is that, speaking HTTP and serving documents, is what people mean by
a **web server** in the narrow sense. Nginx and Apache are the two everybody has
heard of, and they are the same idea as your file server with thirty years of
work on top.

In chapter 12 the server stops reading files and starts running your code to
produce the answer. At that point it is doing a different job, and the name for
the program running your code is an **application server**. Chapter 13's FastAPI
is one.

In production both are usually present at once. Nginx sits in front, holding the
connections, handling encryption, and serving the files that never change. It
passes everything else to the application server behind it, which runs the code.
They are split because they are good at different things, and because the front
one can go on answering while the back one is restarted.

Keep the question "which server" available. When a piece of writing says the
server does something, it is usually worth knowing whether the thing being
described is a rack, a program serving files, or a program running application
code.

## Check it yourself: one machine, many servers, one port each

The claim that a machine can hold any number of servers, but that a port can
hold one, is checkable in fifteen lines. The file is
[`code/11-server-as-hardware-server-as-software/two_at_one_port.py`](../code/11-server-as-hardware-server-as-software/two_at_one_port.py).

```python
import socket


def claim(port):
    """Try to become the program that answers on this port."""
    listening = socket.socket()
    listening.bind(("127.0.0.1", port))
    listening.listen(5)
    return listening


first = claim(8200)
print("claimed port 8200")

second = claim(8201)
print("claimed port 8201 as well, on the same machine")

try:
    claim(8200)
except OSError as refused:
    print(f"asking for port 8200 again: {refused.strerror}")

first.close()
second.close()
```

```
$ python3 two_at_one_port.py
claimed port 8200
claimed port 8201 as well, on the same machine
asking for port 8200 again: Address already in use
```

One process here is holding two ports, and a machine could hold thousands. The
third attempt is refused, and the refusal comes from the operating system rather
than from any agreement between programs. Chapter 9 explained why: the port is
how the operating system decides which waiting program an arriving connection
belongs to, so allowing two claims on one number would leave it with a question
it could not answer.

If either of those numbers is already taken on your machine, the program will
fail on the first call rather than the third. That is the same message telling
you the same thing, and picking a different number fixes it. Ports being
occupied by things you forgot you installed is a normal part of this work.

## Naming things does not add capability

The words are sorted out, which is worth something, and the program is exactly
as capable as it was at the end of chapter 10.

It still hands every visitor the same bytes. There is no way for a page to
greet somebody, or to show one person their own messages and another person
theirs, or to accept anything a visitor types. A website in 1993 was this, and
for a few years that was the whole medium: documents on disks, handed out
unchanged.

The moment a page needs to differ from one visitor to the next, reading a file
stops being enough. Something has to run, per request, and produce the answer.

That change sounds small. It is the largest single step in this tutorial, and
the next chapter is deliberately uncomfortable, because the point of it is to
make you feel every piece of work that a framework will later take away.

---

[Previous chapter](./10-a-web-server-in-one-file.md) | [Next chapter](./12-from-reading-files-to-running-code.md)
