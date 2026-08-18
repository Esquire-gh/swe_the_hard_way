# Software engineering the hard way

A free tutorial that teaches web software engineering from the ground up.

Most tutorials start you in the middle. They hand you a framework, tell you to
run a command, and a website appears. It works, and you have no idea why. Then
every problem you hit afterwards is a problem underneath the layer you were
taught, so you cannot reason about any of it.

This one starts at the bottom. A computer is a machine that follows
instructions. That is the first sentence, and everything else is built on it.
By the end you will have written a web server from raw sockets, understood why
frameworks exist by feeling the pain they remove, and be able to explain what
happens between pressing enter in a browser and seeing a page, at every layer,
without hand waving.

It is free, it is text, and it runs on a normal laptop.

## How to read it

Read it in order. Every chapter answers a question the previous chapter left
you holding, and ends by breaking what it just built. That break is the next
chapter. Skipping around will not work, because the questions will not be
there.

## The chapters

**Part one: one computer**

1. [What it means to tell a computer what to do](./chapters/01-what-it-means-to-tell-a-computer-what-to-do.md)

**Part two: how the machines got connected**

2. [How networks came about](./chapters/02-how-networks-came-about.md)
3. [How networks made the web possible](./chapters/03-how-networks-made-the-web-possible.md)
4. [A website is a file on someone else's computer](./chapters/04-a-website-is-a-file-on-someone-elses-computer.md)

**Part three: the conversation**

5. [The client server model](./chapters/05-the-client-server-model.md)
6. [Requests and responses are just text](./chapters/06-requests-and-responses-are-just-text.md)
7. [Why we need browsers](./chapters/07-why-we-need-browsers.md)

**Part four: building the server**

8. [How a server receives a request](./chapters/08-how-a-server-receives-a-request.md)
9. [What a socket is](./chapters/09-what-a-socket-is.md)
10. [A web server in one file](./chapters/10-a-web-server-in-one-file.md)
11. [Server as hardware, server as software](./chapters/11-server-as-hardware-server-as-software.md)
12. [From reading files to running code](./chapters/12-from-reading-files-to-running-code.md)
13. [What a framework is for](./chapters/13-what-a-framework-is-for.md)
14. [Two people at once](./chapters/14-two-people-at-once.md)

**Part five: everything on top**

15. [Where the data lives](./chapters/15-where-the-data-lives.md)
16. [What makes real systems hard](./chapters/16-what-makes-real-systems-hard.md)
17. [More than one machine](./chapters/17-more-than-one-machine.md)
18. [AI systems are the same systems](./chapters/18-ai-systems-are-the-same-systems.md)

## What you need

A laptop, a terminal, and Python 3. Nothing else, and nothing is installed
until a chapter has explained why the thing being installed needs to exist.
Chapters 1 to 12 and 14 to 18 use only the standard library. Chapter 13 is the
first one that installs anything, and it argues for every package first.

The commands are written for macOS and Linux. On Windows, use WSL.

## Who this is for

Anyone who can already write a small program in some language and wants to know
what is underneath everything they use. You do not need a computer science
degree. You do need patience, because this takes the long road on purpose.

## Running the code

Every listing printed in a chapter is a real file under
[`code/`](./code/), named after the chapter it belongs to, and every
output shown was produced by running it. Run them from their own directory:

```sh
cd code/01-what-it-means-to-tell-a-computer-what-to-do
python3 machine.py
```

Some of them are servers. Those print the address they are listening on and
keep running until you stop them with control C, and the chapter tells you what
to do from a second terminal window.

Chapter 13 is the only one that needs anything installed:

```sh
cd code/13-what-a-framework-is-for
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app:app --port 8000
```

Your numbers will not match the ones printed in the chapters, and they are not
meant to. Where a measurement depends on your machine, the chapter says so and
says which part of the result is the claim.

## The state of this repository

All eighteen chapters are written. See `docs/` for the reasoning behind the
structure and the rules the writing is held to.

- [`docs/BRIEF.md`](./docs/BRIEF.md) is why this exists and what already exists online.
- [`docs/OUTLINE.md`](./docs/OUTLINE.md) is the chapter by chapter plan.
- [`docs/STYLE.md`](./docs/STYLE.md) is the writing contract.
- [`docs/HANDOFF.md`](./docs/HANDOFF.md) is the instruction set it was written against.

Prose and links are checked by a program rather than by eye:

```sh
python3 scripts/check.py
```

## Licence

Free to read, free to share, free to teach from. See [`LICENSE`](./LICENSE).
