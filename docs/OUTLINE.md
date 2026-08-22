# The outline

An introduction and eighteen chapters in five parts. Each chapter below lists
the question it opens with, the idea it delivers, and the limit it hits at the
end. That limit is the next chapter's question. If a chapter cannot state its
closing limit, the chapter is not ready to be written.

A title names the topic plainly, so that the list of titles on its own says
what the course covers. The story lives in the content, where each idea is
explained in plain words and then named with its technical term.

## Introduction

Who this is for: somebody who has followed the tutorials and still cannot
build their own thing. What the hard way means: doing what tutorials let you
skip. Why the focus is the web, what other kinds of software exist, and why an
AI system is software engineering at its core.

## Part one: one computer

### Chapter 1. Computers, programs, and programming

Question: what is actually happening when you run a program.

Idea: programming is telling a machine what to do, and a computer is a machine
that follows instructions one at a time. A program on disk is a file. Running
it means the operating system makes a process, gives it memory, and takes
turns letting the processor work through its instructions.

Limit: this only ever describes one machine, alone.

## Part two: the machines get connected

### Chapter 2. Computer networks

Question: how do two computers reach each other at all.

Idea: moving bytes between machines, why wires alone were not enough, and how
packet switching and layered protocols solved it.

Limit: a network gets bytes from one machine to another, and does not say what
those bytes mean.

### Chapter 3. The web

Question: given a network, what did people build on top of it, and why did the
web win.

Idea: the web as one application among many a network allows. Documents that
link to each other, hosted anywhere, readable by anyone, with nobody's
permission needed.

Limit: readable by anyone skips over how you find them.

### Chapter 4. What is a website?

Question: where does a web page physically live.

Idea: a file on a disk in a machine you do not own. Addresses, routing, and
DNS as the delegation that turns a name into an address.

Limit: knowing where the file is does not explain who asks for it and who
hands it over.

## Part three: the conversation

### Chapter 5. Clients and servers

Question: who is who in this exchange.

Idea: the one who starts the conversation is the client and the one who
answers is the server. This is the client server model. It is a role decided
by who initiated the request and who returned the response, not a kind of
machine, and any machine can be either at any moment.

Limit: the roles do not say what the two sides actually say to each other.

### Chapter 6. Requests and responses

Question: what does a request literally look like on the wire.

Idea: a request and a response are text in a strict format. The format is HTTP
and the document that comes back is usually HTML. Read both byte by byte until
there is no mystery left.

Limit: if it is only text, something has to write it, send it, and draw the
result.

### Chapter 7. Web browsers

Question: why not send the text yourself.

Idea: you can, and the chapter does. A browser adds writing the request
correctly, fetching the parts, drawing the result, and agreeing with every
other browser on what the result should look like.

Limit: the whole part has been about the side that asks. Now the side that
answers.

## Part four: building the server

### Chapter 8. Web servers

Question: what is a web server, actually.

Idea: a long running program that waits. The accept loop, the request response
cycle, and the difference between polling and blocking.

Limit: waiting for the network is something the program has to ask the
operating system for.

### Chapter 9. Socket programming and the Linux socket API

Question: how does a program talk to the network.

Idea: the operating system owns the network card and hands the program a
handle. A socket is a file descriptor that behaves enough like a file that
read and write work on it, identified by a four tuple.

Limit: this is an idea until you use it.

### Chapter 10. Building a static web server

Question: can I really build this myself.

Idea: yes. Accept a connection, read the request, map the request path to a
file path under a folder, return the file or a 404. That is a static web
server, and the path traversal bug is the first thing a stranger will try.

Limit: it sends the same bytes to everybody, one visitor at a time.

### Chapter 11. Building a dynamic web server

Question: what happens when the page depends on who is asking.

Idea: static against dynamic servers. Routing, query strings, forms, escaping
what strangers type, post then redirect then get, cookies and sessions, every
one written by hand and every one more work than it looks. This chapter is
deliberately uncomfortable.

Limit: one malformed line takes the server down, and the tedious code is the
same in every application ever written.

### Chapter 12. Servers as hardware and software

Question: when people say server, which one do they mean.

Idea: the box in a rack and the program running on it, virtual machines and
containers, web servers and application servers, and why two programs cannot
hold one port.

Limit: the program still answers one visitor at a time.

## Part five: more users, more machines

### Chapter 13. Handling multiple users at once

Question: what happens when a second visitor arrives.

Idea: watch the one at a time server make a fast visitor wait for a slow one.
A thread per visitor fixes it in six lines and introduces the race condition,
the lock, the deadlock, Python's interpreter lock, and the event loop by name.

Limit: the data lives in one process's memory, touched by many threads.

### Chapter 14. Introducing databases

Question: how do you keep things after the process exits, and keep them
correct while several people write.

Idea: try a file first and watch it fail three ways. Everything you would
build next is a database. SQL as a domain specific language, transactions,
indexes, and the third appearance of the injection bug.

Limit: a working system, and everything after this is what happens when it
becomes popular.

### Chapter 15. Scaling web applications

Question: what breaks when a lot of people arrive.

Idea: six pressures, each with a symptom first and a component second. Caches,
queues and workers, supervisors and health checks, reverse proxies and load
balancing, containers, logs and metrics. Closes by counting everything written
by hand since chapter ten.

Limit: that count is what a framework is for.

### Chapter 16. Introducing web frameworks

Question: why does everyone use a framework.

Idea: the first install command, fifteen chapters late. The guestbook rebuilt
on FastAPI and chapter fourteen's database, line by line against chapter
eleven, plus what the framework quietly handles and what it does not.

Limit: one machine has a ceiling.

### Chapter 17. Introduction to distributed systems

Question: what changes when the system spans many computers.

Idea: the three reasons a system spreads, for load, for data and for
capability, and then the list of things that stop being true. No answer is
indistinguishable from every failure, clocks disagree, copies force a choice,
agreement costs a majority, and slow is worse than dead.

Limit: this is where most treatments stop, and the loudest part of the
industry sits on the other side.

### Chapter 18. AI systems are still software

Question: is any of this different for AI.

Idea: no. Training is a process reading files, scheduled by an operating
system, spread across machines with chapter seventeen's problems. A model that
answers is a server behind a queue and a cache, streaming a chunked response.

Ending: the reader can name every layer between pressing enter and seeing a
page, which is what the introduction promised.
