# Chapter 9. What a socket is

## The handle the operating system hands back

Chapter 8 ended with a request that a program has to make. Make me reachable on
this port. Take me off the schedule. Wake me when somebody arrives, and give me
something I can read their text out of and write my answer into.

The last part of that is the interesting one. Whatever the operating system
gives back has to be something a program can hold, pass around, use later, and
have several of at once. This chapter is about what that something is, and the
answer is older than networking and is the reason the rest of this fits
together as neatly as it does.

## A number that stands for something the program cannot touch

When a program opens a file, the operating system does not hand back the file.
It hands back a small whole number.

Behind that number the operating system keeps a table, one per process, and
each row records what the number refers to, how far through it you have read,
and what you are allowed to do with it. Your process holds the number and
nothing else. It cannot read the table, edit it, or see anybody else's.

That should feel familiar from chapter 1. A memory address is meaningful only
inside the process that holds it, and these numbers work the same way. Number 3
in your program and number 3 in mine refer to completely different things, and
neither program can tell.

The number is called a **file descriptor**.

Three of them exist before your first instruction runs, because the operating
system set them up while it was creating the process. Number 0 is standard
input, number 1 is standard output, and number 2 is standard error. When you
call `print`, the text ends up being written to number 1.

This is why redirection works. When you type `python3 thing.py > out.txt`, the
shell arranges for descriptor 1 to refer to that file before it starts your
program. Your program calls `print` exactly as it always did, writes to
descriptor 1 exactly as it always did, and has no idea that anything is
different.

## Everything is a file, which is why this fits

The designers of Unix made that shape the general case rather than a special
case for files.

A regular file on a disk gets a descriptor. So does a named pipe, which is how
chapter 8 could open one with `open` and read it like anything else. So does
the terminal you are typing into, and so do the devices attached to the
machine. All of them are read with the same call and written with the same
call, and that call takes a number and does not ask what kind of thing the
number refers to.

You have been relying on this for as long as you have used a shell. A program
that reads standard input and writes standard output works whether the input is
a keyboard, a file, or the output of another program, and the program contains
no code for any of those cases.

## Berkeley added the network and kept the shape

In 1983 the Computer Systems Research Group at the University of California,
Berkeley, released a version of Unix with TCP and IP built in. They had to
decide what shape networking should have from a program's point of view, and
they chose the shape that already existed.

A network connection would be a file descriptor. The thing that produces one is
called a **socket**.

A connection is not quite a file, so a few new calls had to be added. A file
has a name and a socket has an address, a port, and a protocol. A file is
opened, while a connection is either dialled or answered, and those are
different actions. So the new calls exist to set all that up. Once the
connection exists, reading and writing it are the same reading and writing as
everything else.

Here are the calls a server makes, in the order it makes them.

`socket` asks for a descriptor for talking over a network. What comes back is
not connected or attached to anything yet.

`bind` attaches that descriptor to a particular port on this machine. This is
the line from chapter 8 about telling the operating system you want to be
reachable, and this is where it happens.

`listen` says that this side answers rather than calls. From that moment the
operating system will accept connections on your behalf and hold them in a
short queue, even while your program is busy or has not asked for them yet. How
long that queue may get is a number you pass in, and it stops mattering only
until the day it matters a great deal.

`accept` is the blocking call from chapter 8. It takes the process off the
schedule until somebody is in the queue, and then returns.

What `accept` returns is worth saying loudly, because it is the part people
carry a wrong picture of for years. It returns a **new** descriptor, for that
one conversation. The listening socket is never read from and never written to.
Its only job is to produce conversations, and it goes straight back to
listening. A server therefore has one listening socket and as many conversation
sockets as it currently has visitors, which is the fact chapter 14 is built on.

The client side is shorter. `socket` to get a descriptor, `connect` to dial an
address and port, then read and write, then close.

One practical detail. On Unix systems, ports below 1024 can only be claimed by
privileged programs, which is why real web servers on port 80 are started with
help and why every server in this tutorial uses port 8000 instead.

## Which conversation is which

There is a question that this raises and that most explanations skip.

A busy machine has a thousand browsers connected to port 443 at the same
moment. If a connection were identified by its port, all thousand would be the
same connection and the operating system would have no way to tell whose packet
was whose.

So a connection is not identified by a port. It is identified by four things
together: the address and port at this end, and the address and port at the
other end. The server end is the same for everybody, and the other end differs,
because each client's operating system picks an unused port of its own when it
dials out. Four numbers, unique as a group, and the operating system uses them
to decide which socket an arriving packet belongs to.

## A file and a connection, side by side

The claim of this chapter is that a socket is the same kind of handle as an
open file. That is checkable in about twenty lines. The file is
[`code/09-what-a-socket-is/descriptors.py`](../code/09-what-a-socket-is/descriptors.py).

```python
import os
import socket
import sys

print("standard input  ", sys.stdin.fileno())
print("standard output ", sys.stdout.fileno())
print("standard error  ", sys.stderr.fileno())

opened = open(__file__)
print("this source file", opened.fileno())

connection = socket.socket()
print("a socket        ", connection.fileno())

connection.connect(("info.cern.ch", 80))
request = b"GET / HTTP/1.1\r\nHost: info.cern.ch\r\nConnection: close\r\n\r\n"

# os.write and os.read take a number and know nothing about what it refers to.
os.write(connection.fileno(), request)
answer = os.read(connection.fileno(), 38)
first_line = os.read(opened.fileno(), 38)

print("\nread from the file    ", first_line)
print("read from the socket  ", answer)

opened.close()
connection.close()
```

Running it:

```
$ python3 descriptors.py
standard input   0
standard output  1
standard error   2
this source file 3
a socket         4

read from the file     b'"""A file and a network connection, si'
read from the socket   b'HTTP/1.1 200 OK\r\nDate: Tue, 18 Aug 202'
```

The numbers are the first lesson. Standard input, standard output and standard
error took 0, 1 and 2 before the program started. The file took 3. The socket
took 4. They came out of one counter, because as far as the operating system is
concerned they are one kind of thing, and the socket got the next number that
happened to be free.

The last two lines are the second lesson, and it is the whole chapter. `os.read`
was handed a number and asked for 38 bytes. One of those reads came off a disk
in this laptop and the other came from a machine in Switzerland, and the call
that fetched them is the same call with a different number in it. Nothing in
`os.read` knows or cares which is which.

## Check it yourself: write to your screen by number

If a socket really is the same kind of handle, then the call that just sent an
HTTP request across Europe should also be able to put a line on your screen,
because your screen is descriptor 1.

```
$ python3 -c "import os; os.write(1, b'this went to standard output by number\n')"
this went to standard output by number
```

Then send the same line somewhere else without changing the program at all.

```
$ python3 -c "import os; os.write(1, b'and this went into a file\n')" > /tmp/fd1.txt
$ cat /tmp/fd1.txt
and this went into a file
```

One call, three destinations, no knowledge of any of them.

Then check the four numbers from earlier. This opens three connections to the
same port on the same machine at once. The file is
[`code/09-what-a-socket-is/same_port.py`](../code/09-what-a-socket-is/same_port.py).

```
$ python3 same_port.py
      this machine          the other machine
fd 3   192.168.1.182:59381       188.184.67.127:80
fd 6   192.168.1.182:59382       188.184.67.127:80
fd 7   192.168.1.182:59383       188.184.67.127:80
```

Three separate conversations with one port on one machine, and the only thing
distinguishing them is the number on this end, chosen by the local operating
system out of whatever was free. That is how one server answers a thousand
people on port 443 without any confusion about who is who.

Two smaller things in that output are worth a glance. The descriptor numbers
are 3, 6 and 7 rather than 3, 4 and 5, because they are whatever was free at
the time and nothing promises they are consecutive. And the address at this end
begins `192.168`, which is the private address from chapter 4, so this machine
is reachable from the internet at no address whatsoever and is still holding
three conversations with it.

## An idea you have not used yet

Everything needed is now on the table, and none of it has been put together.

Chapter 8 gave the shape of the loop. This chapter gave the calls that fill the
one line that had no implementation. Chapter 6 gave the text that goes in and
out, and a parser for it in thirty lines. Chapter 4 explained how somebody
finds the machine, and chapter 7 showed a request being typed by hand.

Knowing what `accept` does is not the same as having watched your own process
sit at 0.0 per cent, doing nothing, until a browser you opened yourself made it
wake up and hand back a page you wrote. There is a difference between the two,
and the only way to have the second one is to write it.

It fits in one file.

---

[Previous chapter](./08-how-a-server-receives-a-request.md) | [Next chapter](./10-a-web-server-in-one-file.md)
