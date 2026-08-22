"""Two clocks that disagree, and what that does to keeping the latest write.

Run it with: python3 clocks.py
"""

import time

# Machine B's clock is 120 ms ahead of A's. This is an ordinary amount.
OFFSET = 0.120


def clock_on_a():
    return time.time()


def clock_on_b():
    return time.time() + OFFSET


# B writes first. A writes fifty milliseconds later, so A's value is the newer.
b_write = ("the old value", clock_on_b())
time.sleep(0.050)
a_write = ("the new value", clock_on_a())

print(f"written on B first, stamped {b_write[1]:.3f}")
print(f"written on A after,  stamped {a_write[1]:.3f}")

keep = max([a_write, b_write], key=lambda write: write[1])
print(f"\nkeeping whichever stamp is larger gives: {keep[0]!r}")
print(f"the write that really happened last was: {a_write[0]!r}")

print("\ntime.time can also move backwards when a machine corrects its clock:")
print(f"  time.time      {time.time():.3f}  is the wall clock, and is adjusted")
print(f"  time.monotonic {time.monotonic():.3f}  only ever goes forward")
