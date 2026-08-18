# Chapter 2. How networks came about

## Two machines with nothing in common

At the end of the last chapter we had a process running on one machine, and a
need to get some bytes to a process on another one. Neither of the tools we
had was any use. A memory address is a box number, and box number 4,096 on
your laptop has nothing to do with box number 4,096 on mine. A file is on a
disk, and neither machine can see the other's disk.

So the two processes have nothing in common at all. Whatever gets from one to
the other has to travel outside both of them, through something neither one
owns. This chapter is about what that something turned out to be, and why it
looks the way it does. The design is odd in ways that only make sense once you
know which problem each part was answering.

## Why you cannot just run a wire

Start with the obvious version. Run a wire between the two machines, agree that
a high voltage means one and a low voltage means zero, and send the bytes.

That works, and for two machines it is genuinely all you need. The trouble
starts at three. Three machines that all want to talk to each other need three
wires. Ten machines need forty five. A hundred machines need four thousand nine
hundred and fifty, because every machine needs its own wire to every other one,
which is `n` times `n - 1`, halved.

The arithmetic is bad, but the physical version is worse. Your machine and mine
are not in the same building. A dedicated wire between them would have to be
dug along every road in between, and then dug again for the next pair.

So machines cannot each have their own wire. They have to share, which means
some machines in the middle have to accept traffic that is not for them and
pass it along. Every question in this chapter follows from that one concession.

## The telephone system had already solved this, wrongly

When computer people started worrying about this in the early 1960s, there was
already a working global network for sharing links between many parties. The
telephone system had been doing it for eighty years.

Its method was to build a path and hold it. When you placed a call, the
exchange found a chain of physical links from your phone to the other one and
reserved every link in that chain for you. For as long as the call lasted, that
path was yours. Nobody else could use those links, and your voice had them to
itself. This is called **circuit switching**, and for conversation between two
people it is a good design. The line is steady, it never breaks up, and the
order of what you say is guaranteed by physics.

It suits computers badly, for two reasons.

The first is that computer conversations are mostly silence. A person at a
terminal types a line, then reads the reply for twenty seconds, then types
another. A reserved path is unused for almost all of that, and nobody else is
allowed near it. Human speech has short gaps, so the waste is tolerable.
Machine traffic is a burst, then nothing, then a burst, and reserving a whole
path for it wastes nearly all of what you paid for.

The second reason is that the path is fixed at the start. If any single link in
the chain fails, the call ends. In 1960 that was not an inconvenience but the
central objection, because the people funding this work in the United States
wanted communications that would survive parts of the country being destroyed.

## Chopping the message into packets

Two people solved this separately, for those two different reasons.

Paul Baran, working at RAND in the United States, published the survivability
version in 1964. Build a mesh with many redundant links, cut every message into
small standard sized blocks, and let each block find its own way across. No
path is reserved, so no single break can end a conversation. The traffic goes
around the damage.

Donald Davies, at the National Physical Laboratory in England, reached almost
the same design in 1965 and 1966 from the other direction. He was thinking
about sharing one expensive line between many bursty interactive users, which
is the waste problem rather than the survival problem. He gave the small blocks
the name that stuck. He called them **packets**.

The move that makes it work is small and worth stating on its own. Write the
destination address on every packet. Once each packet carries its own address,
nothing has to be arranged in advance. A machine in the middle receives a
packet, reads the address, decides which of its links points roughly the right
way, and passes it on. Then it forgets about it and handles the next one. A
machine whose job is doing that is a **router**.

Because nothing is reserved, the links are shared from moment to moment. When
your conversation is silent, the capacity you are not using is carrying
somebody else's packets, without anyone arranging it. This is **packet
switching**, and it is the design the internet still runs on.

The first real network built this way was the ARPANET, funded by the American
defence research agency. Its first two machines were connected on the twenty
ninth of October 1969, one at UCLA and one at the Stanford Research Institute.
The first thing anyone tried to send was the word `LOGIN`. The far end crashed
after the second letter, so the first message ever sent across the ancestor of
the internet was `LO`. There were four machines on it by the end of that year.

## What a network actually promises

Packet switching buys sharing and survival, and it is worth being exact about
what it costs, because everything in the rest of this chapter is built to pay
that cost back.

If every packet finds its own way, then packets from the same message can take
different routes. Different routes take different amounts of time, so they can
arrive in a different order from the one they left in. A router with more
traffic than it can forward throws packets away, so some do not arrive at all.
Nothing is watching the message as a whole, because no machine in the middle
knows the message exists.

Here is that, made small enough to look at. The file is
[`code/02-how-networks-came-about/packets.py`](../code/02-how-networks-came-about/packets.py).

```python
import random

MESSAGE = "a network does not deliver messages, it delivers packets"
SIZE = 8
LOSS = 0.15

random.seed(7)   # so the run prints the same thing for everybody


def chop(message, size):
    """Cut the message into numbered pieces."""
    pieces = [message[at:at + size] for at in range(0, len(message), size)]
    return list(enumerate(pieces))


def network(packets):
    """Deliver packets the way a real one does. Not in order, and not all."""
    delivered = [packet for packet in packets if random.random() > LOSS]
    random.shuffle(delivered)
    return delivered


sent = chop(MESSAGE, SIZE)
arrived = network(sent)

print("sent    ", [number for number, _ in sent])
print("arrived ", [number for number, _ in arrived])

print("\nin the order they turned up:")
print("   " + "".join(text for _, text in arrived))

print("\nsorted by number:")
print("   " + "".join(text for _, text in sorted(arrived)))

lost = sorted({number for number, _ in sent} - {number for number, _ in arrived})
print("\nnever turned up:", lost)
```

Running it:

```
$ python3 packets.py
sent     [0, 1, 2, 3, 4, 5, 6]
arrived  [4, 2, 0, 1, 5]

in the order they turned up:
   ges, it ot deliva network does ndelivers

sorted by number:
   a network does not delivges, it delivers

never turned up: [3, 6]
```

Read the three outputs in order, because they are three different lessons.

The first is what the receiving machine is actually handed. It is not a
message. It is a heap of fragments in an order nobody chose, and reading them
as they arrive produces nonsense.

The second is what the numbers buy. Sorting by the number written on each
packet puts the fragments back in the order they were written, without anyone
in the middle having tracked anything. That number is the entire reason
reassembly is possible.

The third is the part that cannot be fixed by sorting. Packets 3 and 6 are not
late, they are gone, and the sorted text has a hole in it where packet 3 should
be. But look at what the receiver knows. It has 0, 1, 2, 4, 5 and it can see
that 3 is missing, because the numbering told it what to expect. Knowing that
something is missing is not the same as having it, and it is the thing you need
before you can ask for it again.

## Who fixes it, and where

By the early 1970s the ARPANET was working, and a second problem had appeared
behind the first. There was now more than one network. There was a packet radio
network, a satellite network, and several others, each with its own rules, its
own maximum packet size, and its own ideas about reliability. They could not
talk to each other.

Vint Cerf and Bob Kahn published the answer in 1974, and its central move is a
refusal. Assume nothing about the networks underneath. Do not require them to
be reliable, or fast, or to agree on anything. Put a machine at the join
between two networks to pass packets from one into the other, give every
machine an address in one shared scheme that spans all of them, and let each
network carry the packets however it likes internally.

That gives a network of networks, which is where the name internet comes from.
It also forces a decision about where the fixing happens, and the decision they
made is the reason the thing is still standing fifty years later.

The middle stays ignorant. A router's whole job is to look at one packet, pick
a link, and forward it. It does not know what conversation the packet belongs
to, whether earlier packets arrived, or what any of it means. Everything about
ordering, loss and retransmission is dealt with only by the two machines at the
ends. This is called the **end to end principle**. It is why the middle of the
internet has never had to be upgraded to understand the web, or video calls, or
anything else invented after it was built. The middle does not understand any
of them. It moves packets.

In 1978 the design was split into two pieces, because not every program wants
the same promises.

**IP**, the Internet Protocol, is the modest half. It carries one packet
towards an address. It may lose it, deliver it twice, or deliver it after the
one behind it. It makes no promises and it runs everywhere, including on every
router in the middle.

**TCP**, the Transmission Control Protocol, is the demanding half, and it runs
only on the two machines at the ends. It numbers the bytes it sends. The
receiver sends back short notes saying how far it has got. Anything not
acknowledged after a while is sent again, and anything arriving out of order is
held until the gap in front of it is filled. What comes out the far side is an
ordered, complete stream of bytes, delivered in the order they were written.

That is the listing you just ran, made automatic and made continuous. The
sorting is the sequence numbers. Noticing that packet 3 never arrived is what
triggers the request to send it again.

These pieces stack, and the stacking is deliberate. The bottom layer, Ethernet
or Wi-Fi, moves a chunk of bytes to the next machine on the same local link. IP
uses that to move a packet across many joined networks to an address. TCP uses
that to give two programs an ordered, reliable stream. Each layer takes the
promise underneath it and offers a better promise upward, and each one is
allowed to know nothing about the others.

The payoff is replacement. Wi-Fi did not exist when IP was designed, and adding
it changed nothing above the bottom layer. On the first of January 1983 the
ARPANET switched over to TCP and IP in a single day, and the network that
resulted is the one you are on now.

## Check it yourself: count the machines in the middle

The claim that your packets pass through machines run by strangers is easy to
say and easy to check. `traceroute` sends packets with a deliberately short
lifespan. Each packet carries a count of how many machines it is allowed to
pass through, every machine that forwards it lowers that count by one, and the
machine that lowers it to zero throws the packet away and sends back a
complaint. Send one packet allowed one hop, then one allowed two hops, and the
complaints name the machines along the route in order.

```
$ traceroute -m 12 -q 1 example.com
traceroute to example.com (172.66.147.243), 12 hops max, 40 byte packets
 1  the router in this building (192.168.1.1)  3.174 ms
 2  the first machine at the internet provider  63.084 ms
 3  another machine at the same provider  23.595 ms
 4  a machine belonging to a larger carrier  15.053 ms
 5  the edge of that carrier's network  25.749 ms
 6  a machine at the company hosting the site  14.499 ms
 7  172.66.147.243 (172.66.147.243)  10.049 ms
```

The names of the machines in the middle have been replaced with descriptions
here, because the real ones name an internet provider and roughly where the
author lives. Your own run will print the real names, which is itself worth
noticing.

Three things in that output are worth sitting with.

There is no wire from this machine to that one. There are six machines in
between, owned by at least three different companies, none of which has any
relationship with the author or with the site being reached. Each one accepted
a packet that was not addressed to it and passed it on, which is the concession
from the beginning of this chapter, made concrete.

Some machines will not answer. Runs often contain lines of `* * *` where a
machine declined to send the complaint back. Packets still pass through those
machines perfectly well. Being invisible to `traceroute` and being absent are
different things.

Run it twice and the route may change. Nothing has been reserved, so nothing is
obliged to stay the same.

## What the network still does not tell you

We now have what chapter 1 was missing. A process on this machine can hand
bytes to a process on a machine somewhere else, in order, without losses, and
without either of them owning any of the wire in between.

What we do not have is any idea what the bytes mean.

The network moves numbers. It has no opinion about whether a run of 4,206 bytes
is a photograph, a price, a login attempt, or a poem. TCP will deliver them
faithfully and in order, and then the receiving program is holding 4,206 bytes
and has to decide, on its own, what it has just been given. Two programs that
disagree about what the bytes mean will both work perfectly and understand
nothing.

So a network on its own is not useful. What is useful is the agreements people
build on top of it about what the bytes mean, and there have been many of them.
Electronic mail was one, and it is older than the web. File transfer was
another. News, chat, and a long list of things that no longer exist were
others.

The web was one of these agreements, it arrived late, and there was no obvious
reason for it to beat the ones already established. Why it did is the next
chapter.

---

[Previous chapter](./01-what-it-means-to-tell-a-computer-what-to-do.md) | [Next chapter](./03-how-networks-made-the-web-possible.md)
