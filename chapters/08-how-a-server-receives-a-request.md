# Chapter 8. How a server receives a request

## What waiting means for a program

In every experiment in chapter 7 there was a program on the other end that was
already running. It had been started long before, it was reachable on port 80,
and it answered within a few hundredths of a second of the request arriving.
Chapter 5 said that a server's ordinary condition is doing nothing, and that
seemed reasonable at the time.

Put it next to chapter 1 and it stops seeming reasonable. A process is a
sequence of instructions being carried out one at a time by a processor. So
which instruction is "wait"? There is no operation on any machine that means
pause here until a stranger somewhere in the world decides to connect. A
processor has no idea what a stranger is.

Something has to be happening during those hours of apparent idleness, and what
it is turns out to be the whole subject of the next three chapters.

## The shape of every server ever written

Before the waiting, the shape it sits inside. Written out in ordinary words, a
web server is this.

```
tell the operating system you want to be reachable
forever:
    wait until somebody connects
    read the text they sent
    work out what they are asking for
    write the answer back
    close the connection
```

That is not a simplification of a web server. That is a web server. The one in
chapter 10 has this shape, and so do the large ones that run most of the
internet. What separates them is how much happens inside the line about working
out what they are asking for, and how many of these loops run at the same time,
which is chapter 14 and is the hard one.

Look at the six lines and ask which of them you could write today.

Reading text and writing text you have done since your first program. Working
out what the request means is chapter 6, and it came to thirty lines. Closing
something when you have finished with it is ordinary. Telling the operating
system you want to be reachable is a request you do not yet know how to make,
but you can at least see that it is a request.

That leaves one line with no obvious implementation at all, and it is the
second one.

## Two ways to wait, and only one of them is free

There are exactly two ways for a program to wait for something, and the
difference between them matters more than it sounds.

The first way is to keep asking. Look for the thing, and if it is not there,
wait a moment and look again. The server in chapter 5 did this. It listed a
directory, found nothing, slept for fifty milliseconds, and listed it again,
twenty times a second, all day. This is called **polling**.

Polling works, and it has two costs that pull against each other. The processor
does work every time it looks, including on all the occasions when there is
nothing there. And there is a delay between the moment something arrives and
the moment the program notices, of up to one full gap. Shorten the gap to
reduce the delay and you increase the waste. Lengthen it to reduce the waste and
you increase the delay. There is no setting that is good, only settings that are
wrong in different proportions.

The second way is to hand the problem to the operating system. The program says
what it is waiting for and then stops. The operating system takes the process
off the schedule entirely, in the sense of chapter 1, so it is no longer offered
turns on a processor. When the thing arrives, the operating system puts the
process back on the schedule and it carries on from the instruction after the
one that stopped. Between those two moments the process runs no instructions at
all. This is called **blocking**.

A process that is waiting this way is described as blocked. That is what the
`S` meant in chapter 1's `ps` output, when the counting program was using no
processor and still counting on time.

The difference is not a small optimisation. Blocking costs nothing while
waiting and notices instantly. Polling costs something continuously and always
notices late. Why every program does not just block, then, is the thing this
chapter ends on.

## Measuring the difference

We cannot wait on a network connection yet, because that is chapter 9. So wait
on something we already understand.

A **named pipe** is a thing that looks like a file and has no disk behind it.
One program writes into it, another reads out of it, and the bytes go straight
from one to the other through memory. It appears in a directory listing with a
`p` at the front, where an ordinary file has a dash:

```
$ ls -l demo.pipe
prw-r--r--  1 you  staff  0 Aug 18 00:52 demo.pipe
```

The part that matters here is that opening one for reading does not return until
somebody opens the other end for writing. It is a thing you can block on.

Here are the two ways of waiting, doing the same job. The polling version is
[`code/08-how-a-server-receives-a-request/polling.py`](../code/08-how-a-server-receives-a-request/polling.py).

```python
import pathlib
import time

MESSAGE = pathlib.Path(__file__).parent / "knock.txt"
MESSAGE.unlink(missing_ok=True)

print("watching for knock.txt")
looks = 0
wall_started = time.perf_counter()
cpu_started = time.process_time()

while not MESSAGE.exists():
    looks += 1
    time.sleep(0.005)

wall = time.perf_counter() - wall_started
cpu = time.process_time() - cpu_started

print(f"message: {MESSAGE.read_text().strip()!r}")
print(f"waited {wall:.1f} seconds of wall clock")
print(f"looked {looks} times, and found nothing {looks - 1} of them")
print(f"spent {cpu:.3f} seconds of processor time doing it")
MESSAGE.unlink()
```

The blocking version is
[`code/08-how-a-server-receives-a-request/blocking.py`](../code/08-how-a-server-receives-a-request/blocking.py).

```python
import os
import pathlib
import time

PIPE = pathlib.Path(__file__).parent / "knock.pipe"
if not PIPE.exists():
    os.mkfifo(PIPE)

print("waiting on knock.pipe")
wall_started = time.perf_counter()
cpu_started = time.process_time()

# This line does not come back until somebody writes to the other end.
with open(PIPE) as pipe:
    message = pipe.read()

wall = time.perf_counter() - wall_started
cpu = time.process_time() - cpu_started

print(f"message: {message.strip()!r}")
print(f"waited {wall:.1f} seconds of wall clock")
print("looked 1 time, and found something")
print(f"spent {cpu:.3f} seconds of processor time doing it")
```

`time.perf_counter` measures time passing in the world.
`time.process_time` measures processor time given to this process, which is the
number that matters here.

Start one of them, count to ten, then knock from a second window with
[`code/08-how-a-server-receives-a-request/knock.py`](../code/08-how-a-server-receives-a-request/knock.py).

```
$ python3 polling.py
watching for knock.txt
message: 'hello from the other window'
waited 10.0 seconds of wall clock
looked 1632 times, and found nothing 1631 of them
spent 0.046 seconds of processor time doing it
```

```
$ python3 blocking.py
waiting on knock.pipe
message: 'hello from the other window'
waited 10.0 seconds of wall clock
looked 1 time, and found something
spent 0.000 seconds of processor time doing it
```

Both waited the same ten seconds and both got the message. One of them asked
1,632 times and was wrong 1,631 times. The other asked once.

The processor figures are the ones to sit with. Forty six thousandths of a
second sounds like nothing, and for one program it is. Scale it the way a real
machine would. Two hundred programs waiting like that would spend around nine
seconds of processor time in every ten seconds of clock time, which is roughly
one entire processor running flat out to discover that nothing has happened.
The blocking version scales the other way. Two hundred of those cost two
hundred times nothing.

Then halve the sleep in the polling version and run it again. The count
doubles, the cost doubles, and the program is no more useful than it was.

## Check it yourself: look at the process while it waits

Start `blocking.py` and leave it. In another window, ask the operating system
what it thinks of that process, the way chapter 1 did.

```
$ ps -o pid,stat,%cpu,command -p 71243
  PID STAT  %CPU COMMAND
71243 SN     0.0 python3 blocking.py
```

`S` and `0.0`. This is the same reading chapter 1 got from a program that was
counting once a second, and it means the same thing. The operating system's own
record says this process is not runnable. It is not being offered turns, it is
not looking at anything, and it is not, in any sense the machine recognises,
doing something.

That would be surprising if blocking were a clever kind of fast polling. It is
not. The process really has stopped, and the reason it wakes at the right moment
has nothing to do with the process.

## Why the program cannot do this on its own

We now know what the missing line in the server loop has to mean. Stop this
process, and start it again when somebody connects. There are two reasons a
program cannot carry that out itself, and both come from chapter 1.

The first is that a stopped process is stopped. Somebody has to be running at
the moment the connection arrives, in order to notice it and put the process
back on the schedule. That somebody cannot be the process, because the whole
point is that it is not running. Whoever does the waking is never the one
asleep.

The second is that the thing being waited for is a piece of hardware. The bytes
arrive at a network card. Chapter 1 said the operating system owns the machine
and hands out turns on the processor, and it owns the devices in the same way
and for the same reason. A process cannot read the network card directly, any
more than it can read another process's memory. If it could, every program on
your laptop could read every other program's traffic.

So the line has to become a request to the operating system, along the lines of:
I want to be reachable on this port, wake me when somebody arrives, and take me
off the schedule until then.

A request like that has to give something back. The program needs to hold on to
whatever arrives, read the visitor's text out of it, and write an answer into
it, possibly for a long time and possibly while other things are going on.
Chapter 1 mentioned that the bookkeeping the operating system keeps for a
process includes the list of files it has open. The people who designed this
noticed that a program which can already read from and write to an open file
would need to learn almost nothing to read from and write to a connection, if
the connection were handed over in the same shape.

That handle has a name, and the next chapter is about what it is and what the
operating system is doing behind it.

---

[Previous chapter](./07-why-we-need-browsers.md) | [Next chapter](./09-what-a-socket-is.md)
