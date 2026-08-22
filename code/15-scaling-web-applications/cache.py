"""The same expensive answer, produced every time and then not.

Run it with: python3 cache.py
"""

import time

REQUESTS = 100
built = 0
messages = ["Ada was here", "Grace too"]


def build_page(book):
    """Stands in for reading rows out of a database and rendering a page."""
    global built
    built += 1
    time.sleep(0.005)
    return "<ul>" + "".join(f"<li>{line}</li>" for line in book) + "</ul>"


def timed(work):
    started = time.perf_counter()
    for _ in range(REQUESTS):
        work()
    return time.perf_counter() - started


built = 0
without = timed(lambda: build_page(messages))
print(f"{REQUESTS} requests, no cache     {without:5.2f} seconds, "
      f"page built {built} times")

remembered = {}


# BEGIN cached
def cached_page():
    key = len(messages)         # the bug: counts, does not describe
    if key not in remembered:
        remembered[key] = build_page(messages)
    return remembered[key]
# END cached


built = 0
with_cache = timed(cached_page)
print(f"{REQUESTS} requests, with cache   {with_cache:5.2f} seconds, "
      f"page built {built} times")

# Now change the data in a way the key does not notice.
messages[0] = "Ada was here, and edited it"
print(f"\nthe messages now start: {messages[0]!r}")
print(f"the cached page says:   {cached_page()[4:38]!r}")
print(f"pages built in total:   {built}")
