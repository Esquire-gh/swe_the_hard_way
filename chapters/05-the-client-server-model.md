# Chapter 5. The client server model

## Two programs, and nothing yet settled about either

Chapter 4 got us as far as a machine and a path. There is a computer with a
file on its disk, we can turn a name into its address, and chapter 2 gives us
an ordered stream of bytes between two programs once they are joined up.

What has not been settled is anything about the two programs themselves. One of
them has the file and one of them wants it, and every other detail is open.
Which one starts. Whether the machine holding the file is doing anything at all
while nobody is asking. Whether it knows you exist before you turn up. Whether
both programs have to be running at the same time, and if so, who was there
first.

Those questions have one answer, and it is so widely assumed that it usually
goes unstated. It is worth stating, because almost every design decision in the
rest of this tutorial follows from it.

## One of them was already there

The machine with the file cannot spring into life when you ask for something.
Nothing on it would hear you. For your request to be heard, a program on that
machine has to have been started already, and it has to have been sitting
there, doing nothing, waiting for somebody to arrive.

That gives the two roles.

The program that starts the conversation, because it wants something, is the
**client**. The program that was already running, and answers, is the
**server**.

That is the whole model, and five things follow from it.

A server's ordinary condition is doing nothing. It spends nearly all of its
life waiting, and waiting costs almost nothing, which you measured in chapter 1
when the sleeping process showed no processor use at all and still counted on
time.

A server does not know its clients in advance. It has no list of who might
call. It finds out that you exist at the moment you arrive, and it usually
forgets you again when you leave.

The conversation can only be opened from one end. A server cannot ring you up.
This one shapes an enormous amount of what the web looks like. For years, a
page that wanted to show you a new message had to keep asking whether anything
had happened yet, because there was no way for the server to speak first.

Clients are brief and servers are long lived. A client exists to ask one thing
and then stops. The server was running before it arrived and is still running
after it has gone.

Clients arrive whenever they like, and there are many of them. A server with
one visitor and a server with a thousand are the same program in a different
situation, and dealing with that difference is the hardest part of part four.

## It is a role, not a kind of machine

The word server is used for two things, a program and a physical computer, and
chapter 11 is about untangling that. Everything in this chapter is the program.

The role belongs to the conversation, not to the machine. The same computer can
be a client in one conversation and a server in another at the same instant.
Your laptop is a client while you read a page, and a server if you are sharing
your screen, or running a development server, or letting a phone in the house
print to it. None of those change what the machine is. They change what it is
doing in a particular exchange.

It is worth saying that this arrangement is a convention rather than a law,
because it is so common that it starts to look like one. Nothing in chapter 2
is asymmetric. Any address may send a packet to any other address, and the
routers in the middle do not know or care which end started it. Systems where
every program does both jobs at once are real, and file sharing networks are
the well known example.

Client and server won because it is easier to reason about, and because of the
practical asymmetry from chapter 4. Most machines sit behind a shared public
address and cannot be reached from outside at all. A design where everyone must
be reachable was possible in 1980 and is awkward now.

## Watching the two roles run

We do not yet know how a program listens for someone arriving over a network,
because that is chapters 8 and 9. So here the two programs talk through a
directory on the disk, which is something chapter 1 already covered. The
channel is a placeholder. The roles are the real subject.

The waiting half is
[`code/05-the-client-server-model/waiter.py`](../code/05-the-client-server-model/waiter.py).

```python
import os
import pathlib
import time

MAILBOX = pathlib.Path(__file__).parent / "mailbox"
MAILBOX.mkdir(exist_ok=True)

ANSWERS = {
    "time": lambda: time.strftime("%H:%M:%S"),
    "who": lambda: f"process {os.getpid()}",
}

print(f"waiting for requests in {MAILBOX.name}/ as process {os.getpid()}")

while True:
    for request in sorted(MAILBOX.glob("*.request")):
        question = request.read_text().strip()
        if question in ANSWERS:
            answer = ANSWERS[question]()
        else:
            answer = f"I was not taught the question '{question}'"
        request.with_suffix(".response").write_text(answer)
        request.unlink()
        print(f"asked '{question}', answered '{answer}'")

    # Nothing to do, so give the processor back and look again in a moment.
    time.sleep(0.05)
```

The starting half is
[`code/05-the-client-server-model/asker.py`](../code/05-the-client-server-model/asker.py).

```python
import os
import pathlib
import sys
import time

MAILBOX = pathlib.Path(__file__).parent / "mailbox"
MAILBOX.mkdir(exist_ok=True)

question = sys.argv[1] if len(sys.argv) > 1 else "time"
request = MAILBOX / f"{os.getpid()}.request"
response = request.with_suffix(".response")

request.write_text(question)
print(f"process {os.getpid()} asked '{question}' and is now waiting")

started = time.perf_counter()
while not response.exists():
    if time.perf_counter() - started > 5:
        request.unlink(missing_ok=True)
        print("nobody answered. is waiter.py running?")
        raise SystemExit(1)
    time.sleep(0.01)

print(f"answer: {response.read_text()}")
response.unlink()
```

Start the waiting one in a terminal window and leave it alone:

```
$ python3 waiter.py
waiting for requests in mailbox/ as process 59632
```

Then in a second window, ask it three things:

```
$ python3 asker.py time
process 59672 asked 'time' and is now waiting
answer: 00:38:08

$ python3 asker.py who
process 59673 asked 'who' and is now waiting
answer: process 59632

$ python3 asker.py weather
process 59674 asked 'weather' and is now waiting
answer: I was not taught the question 'weather'
```

While that happened, the first window filled in:

```
asked 'time', answered '00:38:08'
asked 'who', answered 'process 59632'
asked 'weather', answered 'I was not taught the question 'weather''
```

The process ids are the part to read closely. Three separate client processes
ran, 59672, 59673 and 59674, each of which existed for a fraction of a second
and then died. Every one of them was answered by process 59632, which was there
before any of them started and is still there now. That is the asymmetry, in
numbers.

The third answer matters too. The client asked something the server had never
been taught, and the server answered anyway, saying what was wrong. It did not
crash and it did not go quiet. A server that stops working because somebody
sent it something unexpected is a server that any stranger can turn off, and
strangers are the entire audience.

Now replace that directory with a network connection and you have a web server.
That substitution is chapters 8 through 10. Nothing in the shape above changes,
which is the reason for showing it before the machinery arrives.

## Check it yourself: ask when nobody is listening

Stop `waiter.py` with control C, then run the client on its own.

```
$ python3 asker.py time
process 60336 asked 'time' and is now waiting
nobody answered. is waiter.py running?
```

Nothing the client can do will produce an answer. It cannot start the server,
because starting a program on somebody else's machine is not something a
network lets you do, and that is deliberate. The server has to already exist,
which is the claim this chapter opened with, and it fails in exactly the way
that a browser fails when a site is down.

Then look at how many programs on your own machine are currently in the waiting
state. On macOS or Linux:

```
$ lsof -nP -iTCP -sTCP:LISTEN
COMMAND     NAME
rapportd    *:50108 (LISTEN)
ControlCe   *:7000 (LISTEN)
ControlCe   *:5000 (LISTEN)
...and more, from applications you installed and forgot about
```

The names have been trimmed here, because the full list names everything the
author has installed. Run it on your own machine to see yours. The word
`LISTEN` is the operating system's record of a program that has asked to be
told when somebody arrives, which is the mechanism chapter 9 is about.

The point of looking is the count. You did not start most of these and you
would not describe any of them as a server. Being the waiting half of a
conversation is an ordinary thing for a program to do, not a special kind of
software that lives in a data centre.

## What the roles do not tell you

We now know who speaks first, who was there already, and who goes away
afterwards. We know nothing whatsoever about what they say.

In the listing above the client sent the word `time` and got back a string,
which worked because both halves were written by the same person in the same
hour. The web is not like that. The two programs were written by strangers,
years apart, in different languages, and they have never communicated about
anything. A browser written this year has to be able to ask a server written
fifteen years ago for a page, and understand the answer.

That requires an agreement fixed in advance and written down: what the client
sends, byte for byte, what the server may send back, and how each side knows
where the message ends. That agreement has a name, and reading it in full turns
out to be less work than most people expect.

---

[Previous chapter](./04-a-website-is-a-file-on-someone-elses-computer.md) | [Next chapter](./06-requests-and-responses-are-just-text.md)
