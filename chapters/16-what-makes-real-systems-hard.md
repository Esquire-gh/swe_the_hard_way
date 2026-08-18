# Chapter 16. What makes real systems hard

## The system works, and then people arrive

What exists at the end of chapter 15 is a complete piece of software. It
answers many people at once, it runs your code for each of them, and what it
knows survives being switched off.

Everything up to here has been about making it work. This chapter is about a
different problem, which is that it works and then becomes popular.

The way to read this chapter is as a sequence of pressures. Each one is a real
thing that happens, each has a symptom you could measure, and each has an
answer that has a name you have probably heard. The names are worth very little
on their own. Attached to the symptom that produced them, they are worth a
great deal, so the symptom comes first every time.

## Pressure one: the same answer, over and over

The guestbook page reads rows out of a database and turns them into HTML. Say
that takes five milliseconds, which is a modest number.

One visitor a second is nothing. A thousand visitors a second needs five
seconds of work per second of clock time, and chapter 1 measured what a machine
does when asked for more work than it has processors. It does not refuse. It
gets slower for everybody at once.

Now notice something about those thousand requests. Almost all of them produce
identical bytes. The guestbook has not changed between them.

The file is
[`code/16-what-makes-real-systems-hard/cache.py`](../code/16-what-makes-real-systems-hard/cache.py).

```
$ python3 cache.py
100 requests, no cache      0.70 seconds, page built 100 times
100 requests, with cache    0.01 seconds, page built 1 times
```

Keeping an answer so that it does not have to be produced again is called
**caching**, and the place it is kept is a **cache**.

You have already seen one without being told. The response in chapter 6 carried
`Age: 14284` and `cf-cache-status: HIT`, which said that answer had been sitting
in a store for four hours and that no machine belonging to the site had been
involved in handing it over.

The cost arrives in the last two lines of that program.

```
the messages now start: 'Ada was here, and edited it'
the cached page says:   '<li>Ada was here</li><li>Grace too'
pages built in total:   1
```

The data changed and the cached page did not. A cache is only correct if you
have decided in advance when its contents stop being true, and there are two
ways to decide. Throw it away after a fixed period, which is exactly the time
to live from chapter 4's DNS. Or throw it away when the underlying thing
changes, which requires knowing every way it can change, including the ones
somebody adds next year.

Where the cache sits is a separate decision with the same shape as everything
else in this tutorial. Inside your process it is fastest and it belongs to that
process alone, so two processes have two caches that disagree. In a separate
program on the same machine or a nearby one, it is shared, and that program is
a server in chapter 5's sense with its own port and its own protocol, which is
what Redis and memcached are. In front of everything, near the visitor, it is
the `cf-cache-status` line, and your machines never hear about the request at
all.

## Pressure two: work nobody should have to wait for

A visitor signs the guestbook. You would also like to email the people who
subscribed, and produce a small version of any photo they attached, and update
a report.

That is half a second on a good day and thirty seconds on a bad one, and for
all of it the visitor is looking at a blank tab. It is worse than one unhappy
visitor, because chapter 14 explained that their thread is held for the whole
time, and there is a fixed number of those.

The file is
[`code/16-what-makes-real-systems-hard/later.py`](../code/16-what-makes-real-systems-hard/later.py).

```
$ python3 later.py
answering after doing the work:     510.03 ms
answering after writing it down:      0.01 ms

emails sent so far: ['ada@example.com']
emails sent once the worker caught up: ['ada@example.com', 'grace@example.com']
```

The move is to not do the work. Write down that it needs doing, answer the
visitor, and let something else pick it up. The written down list of things to
do is a **queue**, and the program that takes items off it and does them is a
**worker**.

Three costs come with that, and none of them is optional.

The answer changed meaning. It used to say the work is done. It now says the
work has been accepted. If the visitor needs to know when it is really
finished, telling them is a feature you now have to build, and it is usually
larger than the original work.

The worker can fail after taking a job. So the queue cannot hand a job over and
forget it. It has to keep the job until the worker reports success, and give it
to somebody else if that never comes, which means a job can be done twice.
Anything on a queue therefore has to be safe to do twice, and the word for an
operation that can be repeated without changing the result is **idempotent**.
Sending an email is not naturally idempotent, which is why you have received the
same notification twice from real companies.

And the queue in that listing is an object inside one process, so it dies when
the process dies, taking the outstanding jobs with it. That is chapter 15's
problem again, and it has chapter 15's answer. A real queue is a separate
program that writes to a disk.

## Pressure three: the process is not immortal

Chapter 13 showed a stranger stopping a server with one malformed line. Correct
programs die too. The machine reboots for an update, the process is killed for
using too much memory, a disk fills up.

Whatever the cause, the site is down and stays down until somebody notices.

The answer is a program whose entire job is to watch yours and start it again
when it stops, which is a **process supervisor**. On most Linux machines this
is `systemd`, and on a container platform the platform does it.

That introduces a problem that is easy to miss. A program that crashes on
startup and is restarted forever looks, from far away, like a program that is
running. So the supervisor has to be told how to check whether your program can
actually do its job, which means your program needs an address that answers
only when it genuinely works. That is a **health check**, and it is the first
piece of code in this tutorial written for a machine to read rather than a
person.

There is also a consequence that connects back. Restarting empties the memory,
so anything kept in a dictionary is gone. That is why sessions like chapter 12's
belong in a database or a cache rather than in a variable, and why signing out
everybody on every deploy is a mistake people only make once.

## Pressure four: a new version means going down

To install a new version you stop the old process and start the new one.
Between those two moments there is no server.

For a small site that is ten seconds at three in the morning, and it is
tolerable. The real damage is indirect. Because deploying hurts, you deploy
less often, so each deploy carries more changes, so each one is more likely to
break something and harder to work out afterwards.

The obvious fix is to start the new version before stopping the old one, and it
runs straight into chapter 11. Two programs cannot hold port 8000. The
operating system refused, and it refused for a reason that has not gone away.

So something else holds the port. A program sits in front, accepts every
connection from the outside, and passes each request on to whichever of your
processes is currently able to serve it. Start the new version on a different
port, tell the front program about it, let the old one finish the requests it is
already handling, and then stop it. Nobody outside saw anything.

That program is a **reverse proxy**, and when there are several of your
processes behind it, choosing between them is **load balancing**. Nginx is the
usual one, and this is the second job chapter 11 said it had.

This is also where a loose end from chapter 4 gets tied. Your application still
binds `127.0.0.1` and is still unreachable from the internet. The proxy is the
part with the public address, the certificate for `https`, and the exposure to
strangers. Making something public turns out to be a different program's job,
which is why chapters 10 and 15 could ignore it entirely.

## Pressure five: it works on my machine

Your laptop has a particular version of Python and the four packages from
chapter 13. The machine you are deploying to has a different version of Python
and none of them. A colleague's machine has a third combination.

Writing the versions down helps and does not finish the job, because those
packages sit on top of system libraries which are also different, and some of
them are compiled against a particular one.

So ship everything underneath the program along with it. A **container image**
is your code plus the libraries plus the system pieces they need, packaged as
one file that runs the same everywhere. Starting one produces a **container**,
which chapter 11 already defined and which is worth repeating because the
picture people carry is usually wrong.

A container is not a virtual machine and there is no second operating system
inside it. It is ordinary processes as described in chapter 1, scheduled by the
same kernel as everything else on the machine, given a restricted view of the
filesystem and the network so that they behave as though nothing else is there.
That is why a container starts in a fraction of a second and a virtual machine
takes half a minute.

The costs are that images get large, that building them is another step that
can fail, and that the isolation between containers is real but thinner than the
isolation between virtual machines, which matters when the neighbours are
strangers.

## Pressure six: you cannot see what is happening

Somebody says the site was slow yesterday afternoon. You have no way to find
out whether that is true, which part was slow, or whether it is still
happening.

Chapter 12 listed the absence of logging among the things that were still
wrong, and nothing since has fixed it. The first answer is to write down what
happened: one line per request, with the path, the status code, and how long it
took. That is a **log**, and for one machine and a few thousand requests a day
it is enough.

At a thousand requests a second nobody reads lines. So the second answer is
numbers summarised over time, such as requests per second, error rate, and how
long requests took. Those are **metrics**.

One detail there is worth more than the vocabulary. The average is close to
useless. If ninety nine requests take ten milliseconds and one takes five
seconds, the average is sixty milliseconds and looks healthy, while one visitor
in a hundred waited five seconds. What you want is the value that ninety five
or ninety nine per cent of requests came in under, which is why people talk
about p95 and p99 rather than the mean.

The cost of all this is that logs are data at volume. They cost money to keep,
they are the easiest place in a system to accidentally record a password or
somebody's personal details, and a log nobody looks at is a cost with no
benefit.

## Check it yourself: make the cache lie, then stop it lying

Run `cache.py` again and look at the last three lines, where the page
disagreed with the data.

The reason is one expression. The cache is keyed on `len(messages)`, so editing
a message without adding one leaves the key unchanged and the stored page is
handed out again. Change the key to describe the contents rather than count
them:

```python
    key = tuple(messages)
```

Run it again.

```
the messages now start: 'Ada was here, and edited it'
the cached page says:   '<li>Ada was here, and edited it</l'
pages built in total:   2
```

The staleness is gone, and the last line is what it cost. The first version
built one page for everything that happened. This one built two, because an
edit now produces a key it has never seen. Make a hundred edits and it builds a
hundred pages.

That is the whole subject in one expression. A cache key that can never be
stale is a cache key that misses more often, and every real caching decision
sits somewhere between those two runs.

## The pressure this chapter cannot answer

Read back over the six fixes and notice what they have in common.

The cache is in your process or on your machine. The worker is another process
on your machine. The supervisor watches processes on your machine. The proxy
sits in front of processes on your machine. The container holds processes on
your machine. Every answer in this chapter is an arrangement of processes, as
described in chapter 1, on one computer.

One computer has a ceiling. You can buy a bigger one, and that works further
than people usually admit, because machines are much larger than they were. It
still ends. There is a largest machine available, it costs far more than two of
half the size, and while you are using it your entire site is one power supply
away from being off.

So sooner or later the system runs on more than one machine. The moment it
does, things that were quietly true stop being true. Two processes on one
machine share memory, a clock, and a disk, and can be certain about what the
other one did. Two machines share nothing at all, and everything between them
goes over the network from chapter 2, which delivers packets out of order,
loses some, and offers no way to tell a slow machine from a dead one.

That is not the same subject with bigger numbers. It is a different subject.

---

[Previous chapter](./15-where-the-data-lives.md) | [Next chapter](./17-more-than-one-machine.md)
