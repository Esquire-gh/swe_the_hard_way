# Chapter 1. What it means to tell a computer what to do

## What happens between pressing enter and seeing a line

You put one line in a file, type a command, and a word appears.

```
$ python3 hello.py
hello
```

Most people learn to program without ever asking what happened in between. The
word we use for it is "run", and that word explains nothing at all. Something
found a file on a disk. Something copied its contents somewhere else. Something
created a record that did not exist a second earlier, decided when your work
would happen, paused it partway through, started it again, and threw the record
away when it was done. Then the word appeared.

This chapter is about that gap. It is the ground floor of everything that
follows, and it is smaller than it sounds. By the end you should be able to say
what a program is when it is not running, what is different about it when it
is, and who is in charge of the difference.

## A computer follows one instruction at a time

Underneath every piece of software you have ever used there is a part that does
arithmetic and very little else. It is called the processor, and in most
writing it is called the CPU. It can add two numbers. It can compare two
numbers. It can copy a number from one place to another. It can decide which
instruction to look at next. That list is not far off complete. Everything else
you have seen a computer do is built out of those few moves, repeated.

The numbers it works on live in memory. Memory is a very long row of numbered
boxes, each holding a small value. The number of a box is called its
**address**, and an address is how everything inside a computer refers to
everything else. When a program says "the total", what is really there is a box
number.

The processor also keeps one piece of private bookkeeping, and it is the
important one. It holds the address of the next instruction to carry out. That
single number is what turns a pile of instructions into a sequence. Fetch the
instruction at that address, do what it says, move the number on by one, repeat
forever. When a program needs to go back and do something again, one
instruction writes a different value into that number, and the machine carries
on from the new place without noticing that anything unusual happened.

That loop is the whole of computation. There is no cleverness in it and there
is no plan. The machine has no idea what your program is for. It is at one
instruction, it does that instruction, it moves to the next one. A processor in
a laptop does this a few billion times a second, and that speed is the only
reason the result looks like thought rather than like counting.

## A program is a file until something runs it

Before you run it, your program is a file. A file is a named stretch of bytes
sitting on a disk, and there is nothing about those bytes that makes them a
program. Nothing is happening inside `hello.py` while you are not looking at
it. It is as inert as a photograph.

So something has to pick the file up and make it into activity, and that
something is another program. The operating system is the program whose job is
running other programs. It was already running before you typed anything, and
it will still be running after your program has finished.

When you press enter, the operating system does several separate jobs that we
usually smear into the one word "run". It finds the file. It reserves a region
of memory and copies the instructions into it. It reserves more memory for the
values the program will make up as it goes. It writes down which files the
program has open, what it is allowed to touch, and the address of the
instruction it should start at. Then it lets the processor loose on it.

That bundle of memory and bookkeeping is a **process**. A process is a running
program plus everything the operating system has to remember about it. The file
and the process are different things, and keeping them apart is worth the
effort. The file does not change while the program runs. The process is
destroyed when the program ends and the file is exactly as it was. You can
start the same file twice and get two processes that share nothing and cannot
see each other.

There is one more job the operating system does, and it is the one nobody
mentions. Your machine has a handful of processors and a few hundred programs
that all want to be running. So the operating system lets one process use a
processor for a few thousandths of a second, interrupts it, writes down exactly
where it had got to and what numbers it was holding, and hands the processor to
a different process. Later it puts the first one back exactly as it was, and
that process continues without any way of telling it was ever stopped.

Deciding who runs next is called **scheduling**. Saving one process and
restoring another is called a **context switch**. It happens thousands of times
a second, and it is why a machine with eight processors can run three hundred
programs and look like it is doing all of them at once. It is not doing all of
them at once. It is taking turns very quickly.

## A machine small enough to watch

None of that is visible on a real computer, because it happens too quickly and
too far underneath. So here is a machine with the same parts and none of the
speed. It has eight boxes of memory, one number saying where it has got to, and
five instructions. It is written in Python because the point is the shape of
the loop, not the syntax.

The file is
[`code/01-what-it-means-to-tell-a-computer-what-to-do/machine.py`](../code/01-what-it-means-to-tell-a-computer-what-to-do/machine.py).

```python
# Eight numbered boxes. This is the whole memory of this machine.
memory = [0] * 8

# The program. Every line is one instruction, and there are five of them.
program = [
    ("set", 0, 3),       # box 0 holds the number we are counting down
    ("set", 1, -1),      # box 1 holds the amount we add each time
    ("show", 0),
    ("add", 0, 1),
    ("jump_if", 0, 2),   # if box 0 is not zero, go back to instruction 2
    ("stop",),
]

counter = 0   # the number of the instruction that comes next
step = 0

while True:
    instruction = program[counter]
    name = instruction[0]
    step += 1
    print(f"step {step:>2}   counter={counter}   {name:<8} memory={memory[:2]}")

    if name == "set":
        memory[instruction[1]] = instruction[2]
        counter += 1
    elif name == "add":
        memory[instruction[1]] += memory[instruction[2]]
        counter += 1
    elif name == "show":
        print(f"                        output: {memory[instruction[1]]}")
        counter += 1
    elif name == "jump_if":
        counter = instruction[2] if memory[instruction[1]] != 0 else counter + 1
    elif name == "stop":
        break
```

Run it:

```
$ python3 machine.py
step  1   counter=0   set      memory=[0, 0]
step  2   counter=1   set      memory=[3, 0]
step  3   counter=2   show     memory=[3, -1]
                        output: 3
step  4   counter=3   add      memory=[3, -1]
step  5   counter=4   jump_if  memory=[2, -1]
step  6   counter=2   show     memory=[2, -1]
                        output: 2
step  7   counter=3   add      memory=[2, -1]
step  8   counter=4   jump_if  memory=[1, -1]
step  9   counter=2   show     memory=[1, -1]
                        output: 1
step 10   counter=3   add      memory=[1, -1]
step 11   counter=4   jump_if  memory=[0, -1]
step 12   counter=5   stop     memory=[0, -1]
```

The memory printed on each line is how memory stands as that instruction
begins, before it has done its work. That is why step 2 already shows a 3 in
box 0. The instruction on step 1 put it there.

Look at the counter column and nothing else. It reads 0, 1, 2, 3, 4, then 2
again. That jump backwards is the entire mechanism of a loop. There is no
looping instruction and no notion of repetition anywhere in the machine. One
instruction wrote a smaller number into the counter, and the same fetch and
carry out loop that had been running all along walked over the same three
instructions a second time.

Every loop you have ever written compiles down to that. So does every `if`,
every function call, and every method on every object. The processor in your
laptop has a few hundred instructions rather than five, and it is doing this
billions of times a second instead of twelve times in total, but the fetch, do,
advance loop is the same one.

## The same story on your own computer

Now watch a real process rather than a pretend one. This program counts once a
second and does nothing else, which gives you time to look at it from outside.

The file is
[`code/01-what-it-means-to-tell-a-computer-what-to-do/slow_count.py`](../code/01-what-it-means-to-tell-a-computer-what-to-do/slow_count.py).

```python
import os
import time

print(f"my process id is {os.getpid()}")

count = 0
while True:
    count += 1
    print(count)
    time.sleep(1)
```

Start it in one terminal window:

```
$ python3 slow_count.py
my process id is 47638
1
2
3
```

The operating system gave this process a number when it created it, and
`os.getpid` asks for that number back. It is called the **process id**, and it
is how everything outside the process refers to it.

Leave it running and open a second terminal window. The `ps` command prints the
operating system's own record of a process, which is the bookkeeping described
earlier. Ask it about that number:

```
$ ps -o pid,stat,%cpu,rss,command -p 47638
  PID STAT  %CPU    RSS COMMAND
47638 SN     0.0   8992 python3 slow_count.py
```

Four things there are worth reading slowly.

`STAT` starts with `S`, which means sleeping. The program is not using a
processor at all. It asked to be woken in a second and the operating system
took it off the schedule until then. Any letters after the `S` record other
details such as priority, and they differ between machines. `%CPU` agrees: this
process is getting almost none of the processor, and it still counts perfectly
on time.

`RSS` is how much memory the process is holding in RAM right now, in kilobytes.
It is roughly nine megabytes for a program that adds one to a number. Almost
none of that is your code. It is Python itself, loaded into the memory the
operating system reserved when the process was created.

`COMMAND` still names the file. The file is on the disk, unchanged, while this
is going on. Start a second copy in a third window and you will get a different
process id and a second `RSS` of its own. One file, two processes, and neither
one can see the other's boxes.

Stop it with control C when you have looked at it.

## Check it yourself: more programs than processors

The claim in this chapter that you cannot check by reading is the last one:
that the operating system takes turns. So measure it instead.

This program runs the same fixed piece of arithmetic in one process, then in
two at the same time, then four, and so on, timing how long each round takes
from start to finish.

The file is
[`code/01-what-it-means-to-tell-a-computer-what-to-do/turns.py`](../code/01-what-it-means-to-tell-a-computer-what-to-do/turns.py).

```python
import os
import subprocess
import sys
import time

# Enough adding up to take a noticeable moment and nothing else.
WORK = "sum(range(100_000_000))"


def time_copies(copies):
    """Start this many copies at once and wait for all of them to finish."""
    started = time.perf_counter()
    running = [subprocess.Popen([sys.executable, "-c", WORK]) for _ in range(copies)]
    for process in running:
        process.wait()
    return time.perf_counter() - started


print(f"this machine reports {os.cpu_count()} processors")
for copies in (1, 2, 4, 8, 16, 32):
    print(f"{copies:>2} copies took {time_copies(copies):5.2f} seconds")
```

On the machine this was written on:

```
$ python3 turns.py
this machine reports 18 processors
 1 copies took  0.75 seconds
 2 copies took  0.75 seconds
 4 copies took  0.75 seconds
 8 copies took  0.74 seconds
16 copies took  1.37 seconds
32 copies took  3.30 seconds
```

Your numbers will be different, and the digits are not the point. The shape is
the point, and the shape has three parts.

At the start, adding more copies is free. Eight processes finished in the time
one process took, because there were idle processors sitting there and the
operating system had somewhere to put the extra work.

Then there is a knee. After it, the time climbs in proportion to the number of
copies. Doubling from sixteen to thirty two roughly doubled the time, because
there was no longer a free processor for each copy. They were taking turns, and
each one spent part of the round stopped, holding its place, waiting to be put
back.

The knee here arrives before eighteen, and that is worth a sentence. Many
laptops now have two kinds of processor, some fast and some built to use less
power, and the number the operating system reports counts both. So the flat
part ends earlier than the count suggests.

Both ends of that curve would be surprising if the chapter were wrong. If each
program really did own a processor from beginning to end, two copies would take
twice as long as one, and the flat part could not exist. If processors were
unlimited, thirty two copies would cost the same as one, and the climb could
not exist. What you measured is turn taking, seen from the outside.

## What one computer cannot do

Here is everything we have. Instructions in memory, a number saying where we
have got to, an operating system handing out turns, and a disk holding files
that are not doing anything until a process reads them.

All of it is inside one box. The process can read the disk in that machine, use
the memory in that machine, and print to a screen attached to that machine.
Nothing described in this chapter gives it any way to reach something that is
not in the box with it.

That is not a small gap. Almost no software anyone actually uses is like that.
The programs we care about are the ones other people can reach, and other
people are not sitting at your laptop. So a process here has to get bytes to a
process somewhere else, and none of the tools from this chapter help. It cannot
pass a memory address, because box number 4,096 on your machine has nothing to
do with box number 4,096 on anyone else's. It cannot write a file, because it
cannot see the other disk.

Two machines, no shared memory, no shared disk, and a need to move bytes
between them anyway. That problem is the whole of the next chapter.

---

[Back to the front page](../README.md) | [Next chapter](./02-how-networks-came-about.md)
