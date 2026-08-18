# Chapter 4. A website is a file on someone else's computer

## Where the page actually is

The library in chapter 3 turned `-> packets` into a filename in a folder, and
that worked because there was one machine and one folder. The web has neither.
A link written years ago by a stranger has to find one particular machine among
all the machines on earth, and then get one particular file off it.

So start with the plain version of what a web page is, because it is less
mysterious than the word "website" suggests. Somewhere there is a computer. It
is probably in a rented rack in a building with good air conditioning, and it
is running an operating system and processes exactly like the ones in chapter
1. On its disk there is a file. When you visit a page, a program on that
machine reads that file and sends the bytes back to you.

That is the whole of it. The rest of this chapter is about the two hard parts
of that sentence, which are finding the machine and naming the file.

## A web address is two questions in one

Take an address apart.

```
https://example.com/about.html
\___/   \_________/ \________/
  |          |          |
scheme     host       path
```

The **scheme** says which set of rules to use for the conversation. `https`
means the rules described in chapter 6, with the conversation encrypted.

The **host** says which machine to have the conversation with. This is the part
that has to be turned into something the network can route to.

The **path** says what to ask that machine for once you are connected. It looks
like a filename in a folder because in 1991 that is what it was. The program on
the far machine took the path, added it to the end of a directory name, and
read that file off the disk. Much of the web stopped working that way long ago,
and chapter 12 is about when and why, but the shape of the name never changed.

Two questions, then, and the answer to the second one is somebody else's
problem until we have solved the first. Which machine.

## Every machine on the network needs a number

Routers forward packets by looking at the destination written on them, which
means every machine reachable on the internet needs a number that is not shared
with any other. That number is its **IP address**.

The old and still common form is four numbers between 0 and 255, written with
dots between them, like `208.80.154.224`. That is thirty two bits in total,
which allows about 4.3 billion machines. When these were being handed out in the
1980s that seemed generous, because nobody had put "one for every telephone" on
the list. They ran out. The newer form is a hundred and twenty eight bits,
written as groups of hexadecimal digits separated by colons, like
`2620:0:861:ed1a::1`. Most machines now have both.

The part worth understanding is not the format but how anything can route to
them. There are billions of machines and no router could hold a list of them.

Addresses are not handed out one at a time. They are handed out in contiguous
blocks, and a router keeps a table of blocks rather than machines. Its table
says something closer to "anything starting 208.80.152 goes out of link three",
and it holds around a million such ranges instead of billions of addresses. A
packet arrives, the router finds the most specific range that contains the
destination, and sends it that way. That is how the machine at hop three of the
traceroute in chapter 2 could forward a packet towards a machine it had never
heard of and knew nothing about.

## The address on your own machine is probably not public

Look again at the first hop of that traceroute. It was `192.168.1.1`.

Some ranges are set aside as private, including everything starting `192.168`,
everything starting `10.`, and a block in the middle of `172`. They are not
unique, they mean nothing on the public internet, and routers on the internet
will not forward packets addressed to them. Your laptop almost certainly has
one right now, and so does mine, and they may well be the same number.

What makes this work is that the box your internet arrives through has one real
public address, and everything in the building shares it. When your laptop
sends a packet out, that box rewrites the sender's address to be its own public
one, writes down the swap, and undoes it when a reply comes back. This is
called **network address translation**, and it is the reason 4.3 billion
addresses have lasted this long.

There is a consequence worth carrying forward, because it will save confusion
later. This arrangement works in one direction. Your machine can start a
conversation with anything on the internet, and nothing on the internet can
start one with your machine, because there is no address that reaches it. When
you write a working web server in chapter 10 and none of your friends can visit
it, this is why. Writing a server and putting it somewhere the world can reach
are two separate jobs, and only the first one is about programming.

## Nobody can remember numbers, and numbers move

Numbers are correct and unusable. People cannot remember them, and worse, they
change. A site moves to a different machine, or to twelve machines in different
countries, and every link ever written to it should keep working.

So there has to be a layer that turns a name into a number, and the first
version was exactly what you would guess. There was one file listing every name
on the network and the address it belonged to. It was maintained at Stanford
Research Institute, and every machine on the ARPANET downloaded a fresh copy
from time to time.

It failed for the reason chapter 3 has already made familiar. One central thing
that everybody has to coordinate with does not survive growth. The file got
large, it was out of date the moment it was copied, and adding a machine meant
writing to someone and waiting.

The replacement, designed in 1983, splits the names up and hands out authority
over the pieces. It is called the **Domain Name System**, and it is worth
reading a name backwards to see the shape.

In `en.wikipedia.org`, the last part is `org`. A small set of machines called
the root servers know nothing about wikipedia, but they do know which machines
are responsible for `org`. Those machines know nothing about the `en` part, but
they know which machines are responsible for `wikipedia.org`. Those machines,
run by the people who run wikipedia, know the address of `en.wikipedia.org`.

Nobody holds the whole list. Each level knows one thing: who to ask next.
Adding a name inside `wikipedia.org` requires telling nobody outside
wikipedia, in the same way that adding a document to the library in chapter 3
required telling nobody at all.

Your own machine does not walk that chain. It asks one machine, called a
**resolver**, usually run by your internet provider, and the resolver does the
walking and then remembers the answer for a stated number of seconds. That
period is called the **time to live**, and it is why the first lookup of a name
is slow and the next thousand are instant.

One last thing about this, and it is the point of putting the chapter here. All
of that is programs on machines sending each other messages over the network
from chapter 2. The root servers are computers running processes as described
in chapter 1. There is no separate magic layer. It is the same story again, one
level up.

## Looking a name up

Python can ask the operating system to do a lookup, and the operating system
asks the resolver. The file is
[`code/04-a-website-is-a-file-on-someone-elses-computer/lookup.py`](../code/04-a-website-is-a-file-on-someone-elses-computer/lookup.py).

```python
import socket
import sys

NAMES = ["example.com", "wikipedia.org", "localhost", "no-such-name.example"]


def addresses_for(name):
    """Every address this name resolves to, without duplicates."""
    found = socket.getaddrinfo(name, 80, proto=socket.IPPROTO_TCP)
    return sorted({result[4][0] for result in found})


for name in sys.argv[1:] or NAMES:
    try:
        found = addresses_for(name)
    except socket.gaierror as problem:
        print(f"{name:<22} no answer: {problem.strerror}")
        continue
    print(f"{name:<22} {', '.join(found)}")
```

Running it:

```
$ python3 lookup.py
example.com            104.20.23.154, 172.66.147.243, 2606:4700:10::6814:179a, 2606:4700:10::ac42:93f3
wikipedia.org          208.80.154.224, 2620:0:861:ed1a::1
localhost              127.0.0.1, ::1
no-such-name.example   no answer: nodename nor servname provided, or not known
```

Your addresses for the first two will differ from these, and may differ from
each other on consecutive runs. That is the first lesson in the output.

One name is not one machine. `example.com` came back with four addresses here,
two of the old kind and two of the new. A busy site answers with several, and
often with different ones depending on where you are asking from, so that you
are sent to a machine near you. The name is a name for a service, and the
service can be as many machines as it likes.

`localhost` is a special name that every machine has, and it points at itself.
Packets sent to `127.0.0.1` never reach a network card at all. The operating
system loops them straight back into itself. Everything in chapters 8 to 15
will be tested against that address, because it means you can run both sides of
a conversation on one laptop.

The last line fails, and it fails the way a broken link failed in chapter 3. A
name that resolves to nothing is an ordinary answer, handled and reported,
rather than a fault in the system.

## Check it yourself: watch the question get handed down

The claim that no single machine knows the whole list is the one worth
checking. `dig` will show you the chain being walked one step at a time.

```
$ dig +trace +nodnssec wikipedia.org A
.                   56789   IN  NS  a.root-servers.net.
.                   56789   IN  NS  b.root-servers.net.
                    ... eleven more ...
org.                172800  IN  NS  a0.org.afilias-nst.info.
org.                172800  IN  NS  b2.org.afilias-nst.org.
                    ... four more ...
wikipedia.org.      3600    IN  NS  ns0.wikimedia.org.
wikipedia.org.      3600    IN  NS  ns1.wikimedia.org.
wikipedia.org.      3600    IN  NS  ns2.wikimedia.org.
wikipedia.org.      180     IN  A   208.80.154.224
```

If `dig` is not on your machine, `host wikipedia.org` or `nslookup
wikipedia.org` will give you the answer without the journey.

Read it as three questions and an answer.

The first block is the root servers, and every one of them declined to answer
the question. There are thirteen names, `a` through `m`, and each name is
really many machines in many countries answering to the same address. What they
returned is not an address for wikipedia. It is a list of who to ask about
`org`.

The second block is the same move again. The `org` servers do not know
wikipedia's address either. They know who is responsible for `wikipedia.org`.

The third block is wikimedia's own machines, and only at that point does an
address appear.

The numbers in the second column are those times to live, in seconds. The
delegation for `org` is good for 172,800 seconds, which is two days, because
who runs `org` almost never changes. The address itself is good for 180
seconds, because they may want to move it at short notice. That single number
is how a site changes machines without anybody editing a link.

Run the same command twice in a row. The chain will be walked again, but ask
for the plain answer twice with `dig wikipedia.org` and watch the reported
query time collapse on the second attempt. That is the resolver's memory doing
its job.

## Who asks, and who answers

We can now find the machine, and we have a path naming what we want from it. A
name became an address, an address is something routers can move packets
towards, and chapter 2 gave us an ordered stream of bytes between two programs
once they are connected.

What we still have no account of is the conversation itself. Two programs, one
of which has the file and one of which wants it. Something has to happen
between them, and every part of it is undecided. Which one speaks first. Whether
one of them was already running before the other appeared, or whether they
started together. Whether the machine with the file is doing anything at all
when nobody is asking.

Those questions have names, and the names come with a model that is so
established it is rarely explained. Before looking at what the two programs say
to each other, it is worth being exact about who they are.

---

[Previous chapter](./03-how-networks-made-the-web-possible.md) | [Next chapter](./05-the-client-server-model.md)
