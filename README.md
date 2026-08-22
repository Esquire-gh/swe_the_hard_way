# Software Engineering the Hard Way

A free course that teaches software engineering from the ground up, with a
deliberate focus on software for the web.

Read it at **https://esquire-gh.github.io/swe_the_hard_way/**

It is written for somebody who has followed the tutorials, built the todo app
or the Netflix clone, and found that they still cannot build their own thing.
The missing piece is not another framework. It is the fundamentals underneath
every framework, learned well enough that the next higher level idea lands on
something. The hard way means doing the things tutorials let you skip: reading
a request byte by byte, writing a server from a raw socket, watching two
visitors collide, and only then installing the library that hides all of it.

By the end you will be able to explain what happens between pressing enter in
a browser and seeing a page, at every layer, without hand waving, and the last
chapter shows that an AI system is that same stack with different names on it.

## How to read it

Start at the [introduction](https://esquire-gh.github.io/swe_the_hard_way/) and read in order. Every chapter builds
something, then breaks it, and the break is the next chapter's opening
question. Skipping around will not work, because the questions will not be
there.

## The chapters

**Part one: one computer**

1. [What programming really is](https://esquire-gh.github.io/swe_the_hard_way/chapters/01-what-programming-really-is.html)

**Part two: the machines get connected**

2. [Then came networks](https://esquire-gh.github.io/swe_the_hard_way/chapters/02-then-came-networks.html)
3. [And then the web](https://esquire-gh.github.io/swe_the_hard_way/chapters/03-and-then-the-web.html)
4. [A website is a file on someone else's computer](https://esquire-gh.github.io/swe_the_hard_way/chapters/04-a-website-is-a-file-on-someone-elses-computer.html)

**Part three: the conversation**

5. [Clients and servers](https://esquire-gh.github.io/swe_the_hard_way/chapters/05-clients-and-servers.html)
6. [Requests and responses are just text](https://esquire-gh.github.io/swe_the_hard_way/chapters/06-requests-and-responses-are-just-text.html)
7. [Why we need browsers](https://esquire-gh.github.io/swe_the_hard_way/chapters/07-why-we-need-browsers.html)

**Part four: building the server**

8. [What is a server really doing?](https://esquire-gh.github.io/swe_the_hard_way/chapters/08-what-is-a-server-really-doing.html)
9. [What a socket is](https://esquire-gh.github.io/swe_the_hard_way/chapters/09-what-a-socket-is.html)
10. [A static web server in one file](https://esquire-gh.github.io/swe_the_hard_way/chapters/10-a-static-web-server-in-one-file.html)
11. [When the page is different for every visitor](https://esquire-gh.github.io/swe_the_hard_way/chapters/11-when-the-page-is-different-for-every-visitor.html)
12. [Two things called a server](https://esquire-gh.github.io/swe_the_hard_way/chapters/12-two-things-called-a-server.html)

**Part five: more users, more machines**

13. [Can you handle two users at once?](https://esquire-gh.github.io/swe_the_hard_way/chapters/13-can-you-handle-two-users-at-once.html)
14. [Where the data lives](https://esquire-gh.github.io/swe_the_hard_way/chapters/14-where-the-data-lives.html)
15. [Can you handle 10,000 users?](https://esquire-gh.github.io/swe_the_hard_way/chapters/15-can-you-handle-10000-users.html)
16. [Introducing web frameworks](https://esquire-gh.github.io/swe_the_hard_way/chapters/16-introducing-web-frameworks.html)
17. [More than one machine](https://esquire-gh.github.io/swe_the_hard_way/chapters/17-more-than-one-machine.html)
18. [AI systems are the same systems](https://esquire-gh.github.io/swe_the_hard_way/chapters/18-ai-systems-are-the-same-systems.html)

## What you need

A laptop, a terminal, and Python 3. Nothing is installed until a chapter has
explained why the thing being installed needs to exist. Chapters 1 to 15 and
17 to 18 use only the standard library. Chapter 16 is the first one that
installs anything, and it argues for every package first.

The commands are written for macOS and Linux. On Windows, use WSL.

## Running the code

Every listing printed in a chapter is a real file under [`code/`](./code/),
named after the chapter it belongs to, and every output shown was produced by
running it. Run them from their own directory:

```sh
cd code/01-what-programming-really-is
python3 machine.py
```

Some of them are servers. Those print the address they are listening on and
keep running until you stop them with control C, and the chapter tells you
what to do from a second terminal window.

Chapter 16 is the only one that needs anything installed:

```sh
cd code/16-introducing-web-frameworks
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app:app --port 8000
```

Your numbers will not match the ones printed in the chapters, and they are not
meant to. Where a measurement depends on your machine, the chapter says so and
says which part of the result is the claim.

## Building the site

The site is generated by a small Python build with no dependencies. The
chapter bodies live in [`content/`](./content/), the spine in
[`chapters.py`](./chapters.py), the inline diagrams in
[`diagrams.py`](./diagrams.py), and the curated videos and courses in
[`resources.py`](./resources.py). The output under [`site/`](./site/) is
committed, so it opens from a file URL, and it is published to GitHub Pages
on every push to `main`.

```sh
python3 build.py          # regenerate site/
python3 scripts/check.py  # dashes, banned words, line length, links, tokens
```

See [`docs/HANDOFF.md`](./docs/HANDOFF.md) for how the pieces fit and
[`docs/STYLE.md`](./docs/STYLE.md) for the rules the writing is held to.

## Licence

Free to read, free to share, free to teach from. See [`LICENSE`](./LICENSE).
