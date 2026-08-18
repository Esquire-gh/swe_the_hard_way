"""Chop a message into packets, push them through an unreliable network, and
try to put them back together.

Run it with: python3 packets.py
"""

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
