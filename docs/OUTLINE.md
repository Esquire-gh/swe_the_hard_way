# The outline

Eighteen chapters in five parts. The numbering matches the eighteen points in
`BRIEF.md` one to one, so nothing gets quietly dropped or merged.

Each chapter below lists the question it opens with, the idea it delivers, and
the limit it hits at the end. That limit is the next chapter's question. If a
chapter cannot state its closing limit, the chapter is not ready to be written.

## Part one: one computer

### Chapter 1. What it means to tell a computer what to do

Question: what is actually happening when you run a program.

Idea: a computer follows instructions one at a time. A program on disk is just
a file. Running it means the operating system makes a process, gives it memory,
and takes turns letting the CPU work through its instructions. Everything else
in this tutorial is built on this and nothing more.

Limit: this only ever describes one machine, alone. Software that only one
person can reach is not the software we use every day.

## Part two: how the machines got connected

### Chapter 2. How networks came about

Question: how do two computers reach each other at all.

Idea: the problem of moving bytes between machines, why wires alone were not
enough, and how packet switching and layered protocols solved it. Enough of the
history to make the design feel inevitable rather than arbitrary.

Limit: a network gets bytes from one machine to another, but it does not tell
you what those bytes mean.

### Chapter 3. How networks made the web possible

Question: given a network, what did people build on top of it, and why did the
web win.

Idea: the web as one application among many that a network allows. What was
new about it: documents that link to each other, hosted anywhere, readable by
anyone.

Limit: saying documents are readable by anyone skips over how you find them.

### Chapter 4. A website is a file on someone else's computer

Question: where does a web page physically live.

Idea: a page is a file sitting on a disk in a machine you do not own. The
internet is one enormous public network, IP addresses are how machines are
found on it, and DNS is the phone book that turns a name people can remember
into an address a machine can use.

Limit: knowing where the file is does not explain who asks for it and who hands
it over.

## Part three: the conversation

### Chapter 5. The client server model

Question: who is who in this exchange.

Idea: one side has the thing, the other side wants it. The one who starts the
conversation is the client. The one who answers is the server. This is a role,
not a kind of machine, and the same computer can be both.

Limit: knowing the roles does not tell you what they actually say to each
other.

### Chapter 6. Requests and responses are just text

Question: what does a request literally look like on the wire.

Idea: an HTTP request and response are text in a strict format. The rules of
that format are HTTP. The document that usually comes back is HTML. Read a real
request and a real response byte by byte until there is no mystery left.

Limit: if it is only text, something has to write it, send it, and draw the
result.

### Chapter 7. Why we need browsers

Question: why not just send the text yourself.

Idea: you can, and the chapter shows you doing it. What a browser adds is
everything else: writing the request correctly, drawing the result, and
agreeing with every other browser on what the result should look like. The
story of how that agreement became the HTML standard.

Limit: this whole chapter has been about the side that asks. Now look at the
side that answers.

## Part four: building the server

### Chapter 8. How a server receives a request

Question: what is a web server, actually.

Idea: a program that waits. It sits on a machine, listens for someone to
connect, reads their text, and writes text back. Introduce the mechanism that
lets a program wait for the network.

Limit: waiting for the network is not something a program can do on its own. It
has to ask the operating system.

### Chapter 9. What a socket is

Question: how does a program talk to the network.

Idea: the operating system owns the network card, so it hands programs a
handle. That handle is a socket. It behaves enough like a file that you can
read from it and write to it, which is why the model stuck.

Limit: this is an idea until you use it.

### Chapter 10. A web server in one file

Question: can I really build this myself.

Idea: yes. Open a socket, accept a connection, read the request text, write
back a response with headers and an HTML body. Then extend it to read a real
file off disk and return its contents. Almost every language has this same API,
because almost every language is talking to the same operating system.

Limit: it works for one visitor requesting one file, and falls apart on almost
everything else.

### Chapter 11. Server as hardware, server as software

Question: when people say server, which one do they mean.

Idea: a short chapter that separates the box in a rack from the program running
on it. Both are called a server, and confusing them makes the rest of this
subject much harder than it needs to be.

Limit: naming things is useful, but the program still cannot do very much.

### Chapter 12. From reading files to running code

Question: what happens when the page is different for every visitor.

Idea: the move from serving fixed documents to generating them. Forms, methods
other than GET, query strings, sessions, and state. Every one of these is
implemented by hand, and every one of them is more work than it first looks.
This chapter is deliberately uncomfortable.

Limit: at this point you are writing the same tedious code over and over, and
getting it subtly wrong.

### Chapter 13. What a framework is for

Question: why does everyone use a framework.

Idea: rebuild chapter 12 in FastAPI, line by line against the hand written
version, so every piece of the framework maps to a problem the reader already
felt. A framework should feel like relief, not magic.

Limit: the framework hides the hard parts, and the hardest one is still there
underneath.

### Chapter 14. Two people at once

Question: what happens when a second visitor arrives.

Idea: the hand written server can only do one thing at a time. Show it
breaking. Then introduce threads, and what it means for the operating system to
run parts of your program at the same time. Cover the things that go wrong when
two threads touch the same data.

Limit: the server can now serve many people, but it forgets everything the
moment it stops.

## Part five: everything on top

### Chapter 15. Where the data lives

Question: how do you remember things after the program exits.

Idea: files on disk, then why that stops working, then what a database actually
is. A database is a program that stores data on disk, with a server in front of
it that speaks its own protocol, driven by a small special purpose language.
SQL is that language, and the chapter explains what a domain specific language
is before using the term.

Limit: you now have a working system, and everything that follows is about what
happens when it becomes popular.

### Chapter 16. What makes real systems hard

Question: why is there so much more to learn.

Idea: take the working system and apply pressure. More users, more data, slower
answers. Each fix introduces a concept, and each concept is introduced only
after the reader has felt the pain that motivates it. Caching, queues,
background work, containers, and deployment. This is the chapter where system
design thinking starts, and it starts from problems rather than from a list of
patterns.

Limit: every fix here still assumes one machine.

### Chapter 17. More than one machine

Question: what changes when the system spans many computers.

Idea: the moment there is more than one machine, some things become impossible
and others become merely difficult. Why the network is not reliable, why clocks
disagree, what consistency costs, and how the common patterns are all trades
against the same small set of constraints.

Limit: this is where most tutorials stop, and it leaves the newest and loudest
part of the industry unexplained.

### Chapter 18. AI systems are the same systems

Question: is any of this different for AI.

Idea: no. Training is a process on a machine, reading files, scheduled by an
operating system, spread across many machines with the same coordination
problems from chapter 17. Inference is a server, listening on a socket,
accepting requests, returning text, behind a queue and a cache. Walk the whole
stack again with the AI names attached, and show that the reader already
understands it.

Ending: the reader can now explain what happens between pressing enter and
seeing a page, at every layer, without hand waving.
