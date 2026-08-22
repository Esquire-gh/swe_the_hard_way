"""Chop a message into addressed packets and push them through a small
network of routers that forward one hop at a time.

Every packet carries where it is going. No router knows what the message is,
which packets came before it, or that a conversation exists at all.

Run it with: python3 packets.py
"""

import random

MESSAGE = "a network does not deliver messages, it delivers packets"
SIZE = 8
HOLD = 4          # how many packets one router can hold at once
random.seed(7)    # so the run prints the same thing for everybody

# The whole of a router's knowledge: for a destination, which link is closer.
NEXT_HOP = {
    "gate":  {"ada": "north"},
    "north": {"ada": "ada"},
}


def chop(message, size):
    """Cut the message into numbered, addressed pieces."""
    return [{"to": "ada", "number": n, "text": message[at:at + size]}
            for n, at in enumerate(range(0, len(message), size))]


sent = chop(MESSAGE, SIZE)
waiting = {"gate": list(sent)}
arrived, lost = [], []

while waiting:
    onward = {}
    for here, packets in waiting.items():
        random.shuffle(packets)              # they do not queue in the order sent
        kept, dropped = packets[:HOLD], packets[HOLD:]
        lost += dropped
        print(f"{here:<6} held {len(kept)} of {len(packets)}, dropped {len(dropped)}")
        for packet in kept:
            link = NEXT_HOP[here][packet["to"]]
            (arrived if link == packet["to"] else
             onward.setdefault(link, [])).append(packet)
    waiting = onward

print("\nsent    ", [p["number"] for p in sent])
print("arrived ", [p["number"] for p in arrived])
print("\nin the order they turned up:")
print("   " + "".join(p["text"] for p in arrived))
print("\nsorted by number:")
print("   " + "".join(p["text"] for p in sorted(arrived, key=lambda p: p["number"])))
print("\nnever turned up:", sorted(p["number"] for p in lost))
