"""Exercise three: the cache is also how a move goes wrong.

A remembered answer is a bet that nothing has changed. Move the site while
the bet is still running and every lookup returns the old address until the
time to live expires. Shortening the time to live fixes that and costs a
walk of the chain every time instead.

Run it with: python3 stale.py
"""

AUTHORITATIVE = {"en.wikipedia.org": "208.80.154.224"}
NAME = "en.wikipedia.org"


def run(ttl, moved_at, new_address, until):
    """Look the name up once a second, moving the site part way through."""
    cache, hops = {}, 0
    for clock in range(until + 1):
        if clock == moved_at:
            AUTHORITATIVE[NAME] = new_address
            print(f"   t={clock:<4} the site moves to {new_address}")
        remembered = cache.get(NAME)
        if remembered is not None and remembered[1] > clock:
            address, cost = remembered[0], 0
        else:
            address, cost = AUTHORITATIVE[NAME], 3
            cache[NAME] = (address, clock + ttl)
        hops += cost
        if clock in (0, moved_at + 1, until):
            state = "stale" if address != AUTHORITATIVE[NAME] else "correct"
            print(f"   t={clock:<4} answered {address:<16} {state}")
    return hops


print("time to live 300 seconds:")
AUTHORITATIVE[NAME] = "208.80.154.224"
long_ttl = run(300, moved_at=60, new_address="185.15.59.224", until=299)
print(f"   servers asked over 300 seconds: {long_ttl}")

print("\ntime to live 1 second:")
AUTHORITATIVE[NAME] = "208.80.154.224"
short_ttl = run(1, moved_at=60, new_address="185.15.59.224", until=299)
print(f"   servers asked over 300 seconds: {short_ttl}")
