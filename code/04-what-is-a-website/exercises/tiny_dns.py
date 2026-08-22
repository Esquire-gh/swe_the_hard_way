"""Exercise two: the Domain Name System in three dictionaries.

Nobody holds the whole list. Each server knows one of two things: the answer,
or who to ask next. resolve() starts at the root and walks the name backwards
one label at a time, counting how many servers it had to ask.

Run it with: python3 tiny_dns.py
"""

SERVERS = {
    "root": {
        "org": ("ask", "org-servers"),
    },
    "org-servers": {
        "wikipedia.org": ("ask", "wikipedia-servers"),
    },
    "wikipedia-servers": {
        "wikipedia.org": ("answer", "208.80.154.224"),
        "en.wikipedia.org": ("answer", "208.80.154.224"),
        "de.wikipedia.org": ("answer", "208.80.154.224"),
    },
}

TTL = 300               # seconds an answer may be remembered for
cache = {}              # name -> (address, the second it stops being usable)
clock = 0               # a fake clock, so the run is the same every time


def ask(server, name):
    """One question to one server: an answer, a referral, or nothing."""
    return SERVERS[server].get(name)


def resolve(name):
    """Walk the chain from the root. Returns the address and the hops it cost."""
    labels = name.split(".")
    at, hops = "root", 0
    while True:
        hops += 1
        reply = ask(at, name)
        if reply is None:
            for take in range(len(labels) - 1, 0, -1):
                reply = ask(at, ".".join(labels[-take:]))
                if reply is not None:
                    break
        if reply is None:
            return None, hops
        kind, value = reply
        if kind == "answer":
            return value, hops
        at = value


def resolve_cached(name):
    """The same walk, skipped entirely while a remembered answer is still good."""
    remembered = cache.get(name)
    if remembered is not None and remembered[1] > clock:
        return remembered[0], 0
    address, hops = resolve(name)
    if address is not None:
        cache[name] = (address, clock + TTL)
    return address, hops


print("one lookup at a time, no memory:")
for name in ("en.wikipedia.org", "wikipedia.org", "de.wikipedia.org", "nothing.org"):
    address, hops = resolve(name)
    print(f"   {name:<18} {str(address):<16} asked {hops} servers")

ROUNDS = 1000
plain = sum(resolve("en.wikipedia.org")[1] for _ in range(ROUNDS))
cached = sum(resolve_cached("en.wikipedia.org")[1] for _ in range(ROUNDS))
print(f"\n{ROUNDS} lookups of the same name")
print(f"   servers asked without a cache: {plain}")
print(f"   servers asked with a cache:    {cached}")
