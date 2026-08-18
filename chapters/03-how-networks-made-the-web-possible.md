# Chapter 3. How networks made the web possible

## A network that carries anything carries nothing in particular

Chapter 2 finished with a stream of bytes arriving reliably and in order, and
with the receiving program having no idea what they were. TCP delivers 4,206
bytes and expresses no view about whether they are a photograph, a price, or a
poem. Two programs that disagree about the meaning will both work correctly and
understand nothing.

So a bare network is not useful. What is useful is an agreement, made in
advance, about what the bytes will mean. An agreement between two programs
about what to send, in what order, and what it signifies is called a
**protocol**. TCP is one, and its subject is delivery. The interesting ones sit
on top of it, and their subject is whatever people wanted to do.

Many were built. The web was a late one, it had no advantage anybody could see
at the time, and for its first few years it was not even the most popular.
This chapter is about what it had that the others did not.

## What people built before the web

Electronic mail across a network arrived in 1971, when Ray Tomlinson sent a
message between two machines on the ARPANET and picked the `@` sign to separate
the person from the machine they were on. It worked, it spread, and it is still
here. But mail is addressed to a person and lands in their box. There is no way
to write something once and let anyone who is interested come and read it.

File transfer arrived the same year. It fixes exactly that. You put a file on a
machine, and other people connect to that machine and take a copy. This is
closer, and for years it was how software and documents were shared. What it
lacks is any way to get around. You have to already know which machine, then
find your way to the right directory, then know the filename. Nothing inside
one file can tell you about another file.

Usenet arrived around 1980 and carried discussion rather than documents. Gopher
arrived in 1991 from the University of Minnesota, and it came closest of all. It
gave you menus of documents you could walk down into, arranged in a hierarchy
across many machines. For a couple of years it was more widely used than the
web.

Look at what all of them share. In every one of them, a document is a dead end.
You can be sent to a document, or you can pick a document off a menu, but once
you are reading it, the document cannot point anywhere. Whatever structure
exists lives outside the documents, in a directory listing or a menu that
somebody maintains.

## The idea of a link was forty years old already

Text that points at other text was not a new thought. Vannevar Bush described a
machine in 1945 that would let a researcher build trails between documents and
follow them later. Ted Nelson gave the idea its name in 1965 and called it
**hypertext**. Doug Engelbart demonstrated a working system with linked
documents in 1968, along with the mouse and shared editing.

By the late 1980s there were hypertext systems people used every day. Apple's
HyperCard shipped with every Macintosh from 1987. They worked well, and they
had a property in common that turns out to be the whole story. Their links were
guaranteed. The system knew about every link, and it would not let you point at
something that was not there. If a document moved, the links to it were
updated. If it was deleted, the links to it went too.

That guarantee is a good idea and it is what everyone assumed a serious system
had to provide. It also puts a hard ceiling on how far the system can spread,
because keeping every link honest means something has to know about every
document and every link at once. That is workable on one machine. It is not
workable across machines owned by people who have never met.

## What CERN needed, and what Tim Berners-Lee gave up

The problem that produced the web was not a grand vision. It was an
administrative mess at a physics laboratory.

CERN in the late 1980s had thousands of scientists from dozens of institutions,
most of them visiting rather than permanent. They brought incompatible
computers running incompatible operating systems and wrote documents in
incompatible formats. People left constantly and their knowledge left with
them. Tim Berners-Lee, working there as a software engineer, wrote a proposal in
March 1989 that began by pointing out that information at CERN kept getting
lost.

His design has four decisions in it, and each one is a refusal to do something
the established systems did.

The first is that links are allowed to break. A link is a one way pointer
that names a document, and nothing checks that the document exists until
somebody follows it. Nobody maintains a registry. When the target has moved,
following the link fails, and failing is an ordinary outcome rather than an
error in the system. This is where `404 not found` comes from, and it is the
single decision that let the thing span machines nobody coordinated.

The second is that anyone may publish without asking. There is no central list
of documents to be added to and no authority to apply to. You put a file on a
machine, run a program that hands it out, and it is on the web.

The third is that anyone may link without asking. Pointing at somebody's
document requires no permission and no cooperation from them, because a link is
just a name written inside your document.

The fourth is that the format describes the document, not the screen. A page
says that a piece of text is a heading, and each machine decides for itself what
a heading should look like. Given a room full of incompatible computers, that
was not a nicety. It was the only way the same document could be readable on all
of them.

Then in April 1993 CERN put the whole thing into the public domain. Anybody
could implement it, sell it, or build on it, for nothing, forever. That same
year the University of Minnesota announced it would charge licence fees for
running a Gopher server. Gopher had been ahead. Within about two years it was
finished.

The web did not win on elegance. It won because it asked nobody for permission
and cost nothing, and it could do that because Berners-Lee gave up the
guarantee that everyone else thought was essential.

## A library that lets its links break

Hypertext with everything else stripped away is small enough to build. Here is
a library of documents where any line beginning with an arrow names another
document, and nothing anywhere checks that the named document exists.

The documents are in
[`code/03-how-networks-made-the-web-possible/library/`](../code/03-how-networks-made-the-web-possible/library/),
and this is `welcome.txt`:

```
A library of four documents, three of which exist.

Any line beginning with an arrow names another document in this library.
Nothing anywhere checks that the named document is really there.

-> networks
-> packets
-> the-one-that-moved
```

The program that walks it is
[`code/03-how-networks-made-the-web-possible/follow.py`](../code/03-how-networks-made-the-web-possible/follow.py).

```python
import pathlib

LIBRARY = pathlib.Path(__file__).parent / "library"
START = "welcome"


def read(name):
    """The text of a document, or None if there is no such document."""
    path = LIBRARY / f"{name}.txt"
    return path.read_text() if path.exists() else None


def links_in(text):
    """Every line of a document that names another document."""
    return [line[3:].strip() for line in text.splitlines() if line.startswith("-> ")]


to_visit = [START]
seen = set()
missing = []

while to_visit:
    name = to_visit.pop(0)
    if name in seen:
        continue
    seen.add(name)

    text = read(name)
    if text is None:
        missing.append(name)
        print(f"[{name}] there is no document with this name")
        continue

    print(f"[{name}] {text.splitlines()[0]}")
    for target in links_in(text):
        print(f"          points at {target}")
        to_visit.append(target)

print(f"\ndocuments read: {len(seen) - len(missing)}")
print(f"links that point at nothing: {missing}")
```

Running it:

```
$ python3 follow.py
[welcome] A library of four documents, three of which exist.
          points at networks
          points at packets
          points at the-one-that-moved
[networks] A network moves bytes between machines and has no opinion about them.
          points at packets
[packets] A packet is a small block of bytes with a destination written on it.
          points at networks
[the-one-that-moved] there is no document with this name

documents read: 3
links that point at nothing: ['the-one-that-moved']
```

Three things in thirty lines, and all three are the web.

The structure is inside the documents. There is no index and no menu. The only
way to know that `welcome` leads to `networks` is to read `welcome`. Adding a
document to this library means writing a file and having something point at it,
and nobody has to be told.

Links go one way. `networks` points at `packets`, and `packets` points back,
but that is two separate one way links that happen to face each other. Nothing
about the first creates the second. `packets` has no way of knowing who points
at it, which is why finding out who links to a page is a whole industry rather
than a query.

A broken link is a result, not a crash. `the-one-that-moved` is missing and the
walk carries on and finishes. Compare that with a system that guarantees its
links: to make the same guarantee here, every one of these files would have to
be registered somewhere, and creating a file would stop being a private act.

## Check it yourself: take a document away

Move one of the documents out of the library and run the walk again.

```
$ mv library/packets.txt library/packets.txt.away
$ python3 follow.py
[welcome] A library of four documents, three of which exist.
          points at networks
          points at packets
          points at the-one-that-moved
[networks] A network moves bytes between machines and has no opinion about them.
          points at packets
[packets] there is no document with this name
[the-one-that-moved] there is no document with this name

documents read: 2
links that point at nothing: ['packets', 'the-one-that-moved']
```

Put it back with `mv library/packets.txt.away library/packets.txt` when you have
looked.

Nothing else in the library noticed. `welcome` still reads correctly and still
lists three links, one of which now fails. No file had to be edited, no index
had to be rebuilt, and the walk still ran to the end.

That is the trade written out in full. In exchange for accepting that some
fraction of links will be dead at any moment, publishing and linking become
things you can do alone. The web is the largest thing humans have built out of
that one exchange.

## What a name has to name

There is a gap in the library, and it is doing a lot of quiet work.

When a document says `-> packets`, the program turns that into a filename in a
folder on this machine. That is fine here, because there is only one machine and
one folder. On the web there is no such folder. The document being pointed at
might be on a machine in another country, owned by a stranger, and the pointer
has to work anyway.

So a name on the web has to carry more than a filename. It has to be enough to
find one particular machine out of every machine on earth, then ask that
specific machine for one particular file. And it has to do it from a document
that was written years ago by somebody who has never heard of you.

Which raises the question this chapter has been avoiding. When you point at a
page, where is that page actually sitting, and how does anything find the
machine it is sitting on.

---

[Previous chapter](./02-how-networks-came-about.md) | [Next chapter](./04-a-website-is-a-file-on-someone-elses-computer.md)
