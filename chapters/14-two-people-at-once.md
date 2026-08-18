# Chapter 14. Two people at once

## What happens when a second visitor arrives

Chapter 13 ended with something uncomfortable. The framework version of the
guestbook serves two people at the same time, and nothing in the file you wrote
says how. Every other job the framework took over was mechanical, and you could
have kept doing it by hand. This one changes what your code is allowed to do,
and the failures it introduces are not repeatable.

So put the framework down and go back to sockets, where the problem is visible.

## Watching it break

Chapter 10 listed this as the server's first limit and then moved on. Here it
is, with one page that takes a moment to produce. The file is
[`code/14-two-people-at-once/one_at_a_time.py`](../code/14-two-people-at-once/one_at_a_time.py).

```python
def handle(request):
    target = request.split(b" ")[1] if request.count(b" ") >= 2 else b"/"
    if target == b"/slow":
        time.sleep(2)          # stands in for a large file or a slow database
        return response(b"slow page\n")
    return response(b"fast page\n")


listening = socket.socket()
listening.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listening.bind(("127.0.0.1", 8200))
listening.listen(5)

while True:
    conversation, _ = listening.accept()
    conversation.sendall(handle(conversation.recv(65536)))
    conversation.close()
```

The `sleep` is standing in for something real. A large file being read off a
disk, a wait for another machine to answer, or the database query that arrives
in chapter 15. The point is that it is time during which this request cannot be
finished.

Ask for the slow page, wait a third of a second, and then ask for the fast one
from another window.

```
$ curl -s http://127.0.0.1:8200/slow > /dev/null &
$ sleep 0.3
$ curl -s -o /dev/null -w "the fast page took %{time_total} seconds\n" \
    http://127.0.0.1:8200/fast
the fast page took 1.692237 seconds
```

The fast page took one and seven tenths of a second, which is the rest of
somebody else's two seconds. It did no work of its own worth measuring.

Read the loop and the reason is unavoidable. Between `accept` and the next
`accept` sits everything: reading, handling, writing and closing. The second
visitor cannot be accepted until the first is finished, because the line that
accepts them is at the top of a loop the program has not reached.

The queue from `listen(5)` does not rescue this, and it is worth being clear
about what it does instead. The operating system completes the connection on
your program's behalf and holds it. So the second visitor's browser connects
successfully and then sits there, which looks to them like a blank page rather
than an error. When the queue fills, further visitors are refused outright.
The queue converts one failure into another one.

## A second place in the same program

Chapter 1 described a process as memory, some bookkeeping, and the address of
the next instruction to carry out. The last of those is the interesting one
here, because there is nothing that says a process may only have one.

A **thread** is a second such place, inside the same process. It has its own
idea of where it has got to and its own working area for the function calls it
is inside. Everything else it shares: the same memory, the same variables, the
same open files, the same descriptors from chapter 9.

The operating system schedules threads exactly as chapter 1 described for
processes, giving each one turns and switching between them thousands of times
a second. Making a thread is much cheaper than making a process, because none
of the memory has to be set up again. It is not free. Each thread needs its own
working area, usually somewhere between a hundred kilobytes and a megabyte, and
that number decides how many you can have.

## The same server, one thread per visitor

The change to the server is small. Take the body of the loop, put it in a
function, and start a thread that runs it. The file is
[`code/14-two-people-at-once/one_at_a_time_threaded.py`](../code/14-two-people-at-once/one_at_a_time_threaded.py).

```python
def serve(conversation):
    """Everything that used to happen inside the loop."""
    conversation.sendall(handle(conversation.recv(65536)))
    conversation.close()


while True:
    conversation, _ = listening.accept()
    threading.Thread(target=serve, args=(conversation,), daemon=True).start()
```

The loop now does one thing: accept somebody and hand them to a thread. It
returns to `accept` immediately, so the next visitor waits for the length of
one `accept` call rather than the length of somebody else's request.

```
$ curl -s http://127.0.0.1:8200/slow > /dev/null &
$ sleep 0.3
$ curl -s -o /dev/null -w "the fast page took %{time_total} seconds\n" \
    http://127.0.0.1:8200/fast
the fast page took 0.000591 seconds
```

One and seven tenths of a second down to six ten thousandths.

`daemon=True` says these threads should not keep the program alive, so control C
still stops it. Without it, a server with an open connection refuses to exit
and you will be looking for the reason.

Notice what else changed. How many things happen at once is no longer your
decision. It is the visitors' decision. Ten thousand visitors is ten thousand
threads, at a megabyte each, and the machine is finished long before that.
Getting past that limit was a well known problem in the early 2000s and the
answer to it appears at the end of this chapter.

## The bug you just made possible

Threads share memory. That is what makes them cheap and it is the entire
difficulty.

Chapter 12's guestbook kept its messages in a list and its sessions in a
dictionary. With one thread, only one piece of code ever touched them. With a
thread per visitor, several pieces of code touch them at the same instant, and
none of them knows about the others.

The classic failure is any sequence that reads a value, works something out,
and writes it back. The file is
[`code/14-two-people-at-once/race.py`](../code/14-two-people-at-once/race.py).

```python
def count(adds, lock=None, hand_over=False):
    """Every worker adds `adds` to one shared total."""
    total = 0

    def worker():
        nonlocal total
        for _ in range(adds):
            if lock:
                lock.acquire()
            current = total            # read
            if hand_over:
                time.sleep(0)          # let another thread have a turn here
            total = current + 1        # write
            if lock:
                lock.release()

    threads = [threading.Thread(target=worker) for _ in range(WORKERS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return total
```

```
$ python3 race.py
no lock                    wanted  400000   got  400000
no lock, switching often   wanted   20000   got    5050
with a lock                wanted   20000   got   20000
```

Read those three lines in order, because the first one is the frightening one.

The first line is wrong code producing the right answer. Four threads read and
wrote a shared number four hundred thousand times with nothing protecting it,
and the total came out exactly right. Anybody testing this would ship it.

The second line is the same code, with one added instruction that makes the
operating system more likely to switch threads between the read and the write.
Three quarters of the additions vanished. Nothing about the logic changed. What
changed is when the scheduler from chapter 1 chose to take a turn away, and
that is not something your program controls, observes, or can reproduce on
demand.

That is the shape of every concurrency bug. It is present the whole time and it
appears only when the timing is unlucky, which on a quiet machine may be never
and under load may be constantly.

The third line is the fix. A **lock** is an object that only one thread can
hold. A thread that asks for a held lock blocks in the sense of chapter 8,
using no processor, until the holder gives it back. Wrap the read and the write
together and no other thread can get between them.

Locks are not free and they are not safe by default.

Everything inside a lock happens one at a time again, so a lock around too much
work removes the benefit of having threads at all. And if one thread holds lock
A and wants lock B while another holds B and wants A, both wait forever. That is
a **deadlock**, and the usual defence is a rule that every thread takes locks in
the same order.

## What Python's threads actually do

There is something specific to Python here, and leaving it out would give you a
wrong picture.

In the usual Python, only one thread runs Python instructions at a time. There
is a single lock inside the interpreter, the **global interpreter lock**, and a
thread must hold it to execute Python. So four threads doing arithmetic take
about as long as one thread doing four times as much, and chapter 1's
measurement of copies of a program getting real parallelism does not apply to
threads inside one Python process.

That sounds like it should make this chapter pointless. It does not, for a
reason that is worth understanding rather than memorising.

A web server does not spend its time doing arithmetic. It spends its time
waiting, for the network, for a disk, and in chapter 15 for a database. A
thread that is blocked releases that interpreter lock, so the other threads run
while it waits. Threads help precisely where a server actually spends its life,
which is why the measurement above showed the improvement it did.

The interpreter lock is also why the first line of `race.py` came out right. It
makes individual small operations safe by accident. It says nothing at all
about a sequence of them, and read then write is a sequence. Recent versions of
Python can be built without this lock, and most other languages never had one,
and in those the first line would be wrong too. Writing code that depends on it
is writing code that is correct for reasons you did not choose.

## What the framework was doing all along

Now the answer to chapter 13's uncomfortable ending.

FastAPI runs a handler written as a plain `def` in a pool of threads. That is
what you just built, with the improvement that the threads are made once and
reused rather than created per visitor, which is where the ten thousand threads
problem gets its first answer.

Which means chapter 13's guestbook had exactly the sharing problem described
here. Several threads were appending to `messages` and writing to `sessions`.
Those two operations happen to be safe in this Python for the accidental reason
in the previous section. That is luck, not design. Change the code to read the
list, decide something, and then write, and it stops being safe, and it will
keep passing your tests.

There is a second approach to serving many people, and uvicorn itself is built
on it. Instead of a thread per visitor, have one thread hold every connection,
ask the operating system which of them have something ready right now, and do a
small piece of work on each in turn. That is an **event loop**. It avoids the
memory cost of thousands of threads and reaches very large numbers of
connections. The price is that any handler which blocks stops everything,
because there is only one thread to stop. A handler written with `async def`
runs directly in that loop, and a plain `def` handler is put in threads
precisely because the framework must assume it will block.

## Check it yourself: take the sharing away

The claim that the second line of `race.py` is about sharing rather than about
the arithmetic is checkable with one edit. Change `WORKERS` from 4 to 1 and run
it again.

```
$ python3 race.py
no lock                    wanted  100000   got  100000
no lock, switching often   wanted    5000   got    5000
with a lock                wanted    5000   got    5000
```

Same code, same handing over of turns, same missing lock, and nothing is lost.
One thread cannot interleave with itself. The bug was never in the addition.

## What threads cannot fix

The server now serves as many people as the machine can hold, and it is worse
off in one respect than it was an hour ago.

Everything it knows still lives in the memory of one process, and chapter 1
said what happens to that when the process ends. Stop the server and the
guestbook is empty and everyone is logged out. Chapter 13 noticed this and said
no framework could fix it.

What this chapter added is that the same data is now being touched by many
threads at once, so keeping it correct depends on getting a lock right at every
place it is used, forever, including in code written next year by somebody who
has not read this chapter.

Two problems, and one answer to both. The data needs to live somewhere that
outlives the process, and that place needs to already know what to do when
several people touch the same thing at the same moment. Neither of those is
something to build yourself, and the reasons why are the next chapter.

---

[Previous chapter](./13-what-a-framework-is-for.md) | [Next chapter](./15-where-the-data-lives.md)
