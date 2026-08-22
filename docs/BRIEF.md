# swe_the_hard_way

## What this repository is

This is a free, open course that teaches software engineering from the ground
up, with a deliberate focus on software for the web. Not from a framework. Not
from a template. From the point where a computer is just a machine that
follows instructions, all the way to the systems that serve millions of people
and the AI models that run on top of them.

Every chapter answers a question that the previous chapter made you ask. That
is the whole design. You should never be told to type a command whose purpose
you do not already understand.

## Where this came from

The starting point was a question. Is there already a video or a written
tutorial online that teaches web engineering this way, beginning at absolute
fundamentals and building up in one unbroken line of reasoning?

The full question, written out as the original eighteen points, is below. The
short answer to whether it already exists is: no, not as one thing.

## The original eighteen points

The tutorial should explain, in this order:

1. Programming is building software, and what it means to tell a computer what
   to do. How fundamentally all software runs on a single computer. How running
   a program means creating a process, which gets loaded into memory and
   scheduled by the operating system to be processed one statement at a time by
   the CPU.

2. How networks came about.

3. How networks made the web possible.

4. How a website is fundamentally reading a file on a computer that is not
   yours, and how being on the internet as a big public network, along with IP
   addresses and DNS, makes websites publicly accessible.

5. How the client-server model can basically be described as who has the site
   and who is trying to view the site. Initiator of the request versus the
   responder.

6. How requests and responses are just text in a very specific format being
   sent over a network. The format being HTML, and the basic principles behind
   HTTP.

7. Why we need browsers to send requests, and how browsers fuelled the
   standardisation of HTML.

8. How the server receives requests and how it responds. An introduction to web
   servers and socket programming.

9. What a socket is, and how the operating system enables socket programming.

10. How almost every programming language has a basic implementation of the
    socket API, and building a simple web server with it. This shows that
    responses are raw text HTML, and also covers reading a file and returning
    its content.

11. Server as hardware versus server as software, meaning the application
    server.

12. Extending the server from Web 1 to Web 2, and what makes building a server
    hard without using frameworks.

13. The beauty of web frameworks. Using FastAPI as an example to demonstrate
    everything that was built by hand earlier.

14. Building the server from scratch again, this time handling concurrent
    users. An introduction to threads and concurrent programming.

15. Databases for storage. How modern databases are programs that store data on
    disk with a server in front of them, speaking a different protocol, driven
    by a domain specific language.

16. Modern software development. Introducing all the concepts that make modern
    software development hard, and the reasoning behind them, with practical
    examples. Caching, queues, containers, and most of the concepts that fuel
    system design thinking.

17. Introducing distributed systems.

18. How AI systems are just like everything described above, from training to
    inference.

## What already exists online, and what does not

A search of what is currently available found no single course, video, or
written tutorial that covers this arc end to end. The material that exists is
split across four groups that do not talk to each other.

The operating systems people explain processes, memory, and sockets. The
networking people explain packets, IP addresses, and DNS. The web people
explain HTTP, HTML, and frameworks. The system design people explain caching,
queues, and distributed systems. Each group assumes you arrived already caring
about their layer, and none of them explains why the next layer had to exist.

The closest individual resources are these.

Harvard's CS50 is the nearest thing in spirit to points 1 through 15. It starts
with what a computer actually does, then moves through C, Python, SQL, and
finally HTML, HTTP, and Flask. But it moves through the web quickly, never
builds a server from raw sockets, and does not touch points 16 through 18.

Hussein Nasser's course bundle, covering operating systems, network
engineering, and backend engineering, is the best match for points 1 and 8
through 14. He explains how the kernel handles sockets, what happens when a
request arrives, and how connections are held open. It is paid, split across
three courses, and aimed at people who already write code, so it skips the
historical reasoning in points 2 through 7.

freeCodeCamp's HTTP networking course covers points 5 through 7 well, but stays
at the protocol level. It never goes down to the operating system or up to
system design.

There are many good written tutorials for points 8 through 10, the raw socket
server, including step by step guides in Python and C, and CodeCrafters' build
your own HTTP server challenge. These are solid, but they assume you already
know why you would want to do this. They do not build the motivation from
points 1 through 7.

Point 18, framing AI systems as the same story of processes, files, sockets,
and scheduling, does not appear in any fundamentals course. It lives separately
in specialist material.

So the gap is real, and the gap is not a missing topic. It is the missing
thread that connects the topics.

## The objective

Build that thread, publish it as a GitHub repository, and give it away for
free.

The repository should be readable on GitHub with no build step. Someone should
be able to land on the front page, start reading, and follow the whole thing to
the end without installing anything until the chapter that needs it. The code
should be small enough to type by hand and should run on a normal laptop.

That brief was written before the site existed. The course is now published
at https://esquire-gh.github.io/swe_the_hard_way/ as a static site built by
a small Python script with no dependencies. The built pages are committed,
so the repository still opens without installing anything, and the sources
under `content/` and `code/` remain readable on GitHub.

The measure of success is simple. A reader who finishes should be able to
explain, without hand waving, what happens between pressing enter in a browser
and seeing a page. And they should be able to build every piece of it
themselves.

## Sources for the research above

- CS50, Harvard University: https://cs50.harvard.edu/x/
- Hussein Nasser's courses: https://courses.husseinnasser.com/
- Fundamentals of Backend Engineering: https://www.udemy.com/course/fundamentals-of-backend-communications-and-protocols/
- freeCodeCamp HTTP course: https://www.freecodecamp.org/news/http-full-course/
- Building a basic HTTP server from scratch in Python: https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842
- Write an HTTP server from the ground up in Python: https://medium.com/@stephen.biston/write-an-http-server-from-the-ground-up-in-9-minutes-with-python-1fdb9800a26a
