"""A write to the primary, a read from a copy that has not caught up yet.

Replication keeps the same data on more than one machine so reads can be
spread and one machine can die without losing anything. The copy is
brought up to date a moment after the primary, not at the same instant,
and a read served by the copy in that moment sees the old value. This is
one primary, one copy a little behind, and a reader who asks too soon.

Run it with:  python3 replication_lag.py
"""

import threading
import time

primary = {"balance": 0}
replica = {"balance": 0}
LAG = 0.2                      # the copy trails the primary by this much


def replicate():
    """Carry each change to the copy, a little late."""
    while True:
        time.sleep(0.02)
        if replica["balance"] != primary["balance"]:
            time.sleep(LAG)                    # the write is in flight
            replica["balance"] = primary["balance"]


threading.Thread(target=replicate, daemon=True).start()

primary["balance"] = 100      # the write lands on the primary at once
print("wrote balance=100 to the primary")

# A read routed to the copy, the way a load balancer spreads reads.
print(f"read from the copy immediately: {replica['balance']}  (stale)")
time.sleep(LAG + 0.1)
print(f"read from the copy after {LAG}s: {replica['balance']}  (caught up)")
