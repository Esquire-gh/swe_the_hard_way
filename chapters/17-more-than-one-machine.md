# Chapter 17. More than one machine

## What changes when there is more than one machine

Every answer in chapter 16 was an arrangement of processes on one computer, and
one computer has a ceiling. Past it, the system runs on several, and this is
where a lot of writing about software becomes vague.

The vagueness is worth avoiding, because the change is precise. On one machine,
two processes share a clock, a disk, and physical memory, and when one asks the
other to do something either the answer comes back or the whole machine has
gone. Across machines none of that is true. Everything between them travels
over the network from chapter 2, which delivers packets out of order, loses
some, and never tells you how long it will take.

This is not the same subject with larger numbers in it. Specific things that
were reliably true stop being true, and the rest of the chapter is those things
in order of how much trouble they cause.

## The thing that becomes impossible

Your program sends a request to another machine and no answer comes back within
the time you were willing to wait. Here is the complete list of what may have
happened.

The request never arrived. It arrived and the machine failed before doing
anything. It did the work and then failed. It did the work and the reply was
lost on the way back. Nothing failed at all and the machine is slow.

From where you are standing those are identical. There is no message you can
send, no check you can perform, and no cleverness you can apply that separates
them, because every one of those checks is another request that can fail in the
same five ways.

The file is
[`code/17-more-than-one-machine/no_answer.py`](../code/17-more-than-one-machine/no_answer.py).
It runs a slow but perfectly healthy server, and a client that waits half a
second.

```
$ python3 no_answer.py
the client gave up after half a second with no answer
what the client can prove happened: []
what actually happened:             ['/charge-the-card']
```

The card was charged. The client has no evidence of it and never will. Nothing
in either program is broken, and no amount of care in either of them would
change the outcome, because the uncertainty is not in the code. It is in the
arrangement.

Almost everything else in this chapter is a way of living with that sentence.

## Retries, and why chapter 16's word matters everywhere

Since you cannot find out what happened, the only move available is to ask
again. And asking again may cause the work to be done twice.

Chapter 16 introduced **idempotent** as a property that jobs on a queue need.
It is not a queue detail. It is the rule for anything that crosses a machine
boundary, because anything that crosses one may be sent twice by a client that
was never told the first attempt worked.

Getting it is a matter of how you say things. "Add five to the balance" is
wrong twice. "Set the balance to thirty" is right twice. "Apply transfer
`8f2c`" is right any number of times if the far side keeps a note of the
transfers it has already applied, and the client rather than the server has to
choose that identifier, because the client is the only one who knows that the
second attempt is a repeat of the first.

The timeout itself is a choice with no correct answer. Too short and you
abandon work that succeeded and do it again. Too long and you hold threads from
chapter 14 waiting on a machine that is already gone, which is the beginning of
a failure described further down. What you can do is choose the number against
a measurement rather than a feeling, which is what chapter 16's p99 was for.

## Nobody agrees what time it is

The natural way to settle which of two writes is newer is to compare
timestamps. It does not work, and the way it fails is quiet.

The file is
[`code/17-more-than-one-machine/clocks.py`](../code/17-more-than-one-machine/clocks.py).
It has one machine's clock a tenth of a second ahead of another's, which is an
ordinary amount.

```
$ python3 clocks.py
written on B first, stamped 1787030393.891
written on A after,  stamped 1787030393.831

keeping whichever stamp is larger gives: 'the old value'
the write that really happened last was: 'the new value'
```

Machines whose clocks are kept in step are kept in step to within some error,
never exactly, and a machine that has lost touch with its time source drifts.
So whenever the difference between two clocks is larger than the gap between
two writes, keeping the later timestamp keeps the older write. That is data
being discarded with no error reported anywhere, by code that looks correct.

The same program shows the other half of it.

```
time.time can also move backwards when a machine corrects its clock:
  time.time      1787030393.831  is the wall clock, and is adjusted
  time.monotonic 2915175.900  only ever goes forward
```

The wall clock is a number somebody is allowed to change, including backwards.
This is why `time.monotonic` exists, why every measurement in this tutorial used
it or `perf_counter`, and why timing anything with `time.time` is a bug waiting
for a clock correction.

The way out is to stop asking when something happened and start asking what it
knew. If every write carries a record of the writes it had already seen, then
the system can tell the difference between one write that came after another
and two writes made by parties who had not heard of each other. Counters used
that way are called logical clocks. They do not remove the problem, they name
it: the second case is a genuine conflict, and something or somebody has to
decide what the answer is.

## Copies, and a choice you cannot avoid

There are two reasons to keep the same data on more than one machine. One is
that machines fail and you would like the data to survive. The other is that
more copies can answer more readers.

Once there is more than one copy, a write arrives at one of them and a read may
be served by another, and there are exactly two things you can do about it.

The write is not finished until every copy has it. Then every read is correct,
writes take as long as the slowest copy, and if one copy is unreachable you
cannot write at all.

Or the write is finished when one copy has it and spreads afterwards. Then
writes are fast and keep working when a machine is missing, and some reader
somewhere gets an answer that is out of date.

Neither is the wrong answer. They are the two answers to a question that has no
free option.

The sharpest version happens when the network splits the machines into two
groups that cannot reach each other, which is called a **partition** and which
does happen. Each side now knows it cannot see the others and must choose:
refuse to answer, and stay correct, or answer, and risk being wrong. That is
the whole content of the result people call CAP. It is a statement about what
you must give up during a partition, not a menu of three properties from which
you select two.

A system where the copies agree once writing stops and enough time passes is
described as **eventually consistent**. Whether that is acceptable depends
entirely on how long eventually is and on what somebody might do in the
meantime, which is a question about your users rather than about databases.

## Splitting instead of copying, and needing one answer anyway

Copies help reading and help survival. They do nothing for writing or for size,
because every machine still holds everything and every write still goes
everywhere.

So the other move is to split the data up, sending some records to one machine
and some to another according to a key. That is **partitioning**, and the word
**sharding** means the same thing. It buys write capacity and lets the data be
larger than any single machine.

It costs in two ways worth knowing in advance. Any question that spans
partitions has to be asked of several machines and the answers combined, so
questions that were one line become a small distributed program of their own.
And the key has to spread the load, because a key that puts your busiest
customers on one machine has given you all the complexity and none of the
capacity.

Some decisions cannot be eventually consistent. Which machine is currently in
charge. Whether this seat has been sold. For these there has to be exactly one
answer and it has to be agreed on.

The method is voting. A group of machines accepts a decision when more than
half of them have accepted it, and the reason it is a majority rather than a
number is worth seeing. Two groups cannot both contain more than half the
machines, so a split network cannot produce two conflicting decisions. This is
**consensus**, and the two well known descriptions of how to do it are Paxos
and Raft.

The price is exactly what it sounds like. Nothing can be decided unless more
than half the machines are reachable, and every decision costs at least one
trip across the network. Which is why systems use consensus for the small
important things, such as who is in charge and what the configuration is, and
avoid it for every write.

## When slow is worse than dead

Come back to the first section, because it has a consequence that surprises
people who have only run one machine.

A machine that has died is easy. Connections to it are refused immediately, you
find out in a millisecond, and you can do something else. A machine that is
still answering, slowly, is the dangerous one.

Your server calls another service that has become slow. Its threads, in the
sense of chapter 14, fill up with requests that are waiting rather than
working. Since there is a fixed number of them, your server becomes slow.
Whatever calls your server now fills up in the same way. One slow component
takes down everything in front of it, and none of those things are broken.

Retries make it worse rather than better. A service that is struggling starts
receiving more traffic than it did when it was healthy, because everybody who
gave up is asking again.

The answers all have the shape of giving up on purpose. Have a worse answer
ready and use it, such as a cached page or a sensible default. Stop sending
requests to something that keeps failing, for a while, so it can recover, which
is a **circuit breaker**. Decide in advance how many requests you will hold at
once and refuse the rest immediately rather than accepting them and never
answering, which is **backpressure**, and a fast refusal is kinder to everybody
than a connection that hangs. And when retrying, wait longer each time and add
a random amount, because a thousand clients that all retry after exactly one
second arrive as one spike.

## Check it yourself: give the client more patience

Change `client.settimeout(0.5)` to `client.settimeout(3.0)` in `no_answer.py`
and run it again.

```
the client got: HTTP/1.1 200 OK
what the client can prove happened: ['/charge-the-card']
what actually happened:             ['/charge-the-card']
```

Nothing else changed. The same server did the same work and took the same one
and a half seconds. The only difference between a failed request and a
successful one was a number chosen by the client.

That is worth sitting with, because it does not happen inside one process.
There, whether a function returned is a fact about the world. Across machines,
whether a request succeeded is a judgement your client makes from incomplete
information, using a threshold you picked, and it can be wrong in both
directions.

## The part that gets left out

That is the shape of the subject. Nothing can be known for certain, clocks
disagree, copies force a choice between being right and being available,
agreement costs a majority and a round trip, and slow is worse than dead.

Most treatments of this material stop about here, and it is a reasonable place
to stop. The trouble is that the loudest part of the industry sits on the other
side of that stopping point, and the way it is written about makes it sound
like a separate discipline with its own physics.

It is not. A model being trained is a process on a machine, reading files off a
disk, given turns by an operating system, spread across many machines with
precisely the coordination problems in this chapter. A model answering
questions is a server, listening on a socket, accepting requests, and writing
text back, behind a queue and a cache.

The last chapter walks the whole stack again with the other set of names
attached, and the point of it is not to teach you anything new.

---

[Previous chapter](./16-what-makes-real-systems-hard.md) | [Next chapter](./18-ai-systems-are-the-same-systems.md)
