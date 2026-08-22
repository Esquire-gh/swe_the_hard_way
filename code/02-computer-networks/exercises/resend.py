"""Exercise two: ask again for whatever did not turn up, until it all has.

The network is the one from packets.py and is no more reliable. The sender
now keeps a list of what the receiver still lacks and sends only that. This
is retransmission, which is most of what TCP does for you.

Run it with: python3 resend.py
"""

import random

MESSAGE = "a network does not deliver messages, it delivers packets"
SIZE = 8
HOLD = 4
random.seed(7)

NEXT_HOP = {"gate": {"ada": "north"}, "north": {"ada": "ada"}}

sent = [{"to": "ada", "number": n, "text": MESSAGE[at:at + SIZE]}
        for n, at in enumerate(range(0, len(MESSAGE), SIZE))]


def deliver(packets):
    """One trip through the network. Some of these will not make it."""
    waiting, arrived = {"gate": list(packets)}, []
    while waiting:
        onward = {}
        for here, batch in waiting.items():
            random.shuffle(batch)
            for packet in batch[:HOLD]:
                link = NEXT_HOP[here][packet["to"]]
                (arrived if link == packet["to"]
                 else onward.setdefault(link, [])).append(packet)
        waiting = onward
    return arrived


have = {}
rounds = 0
while len(have) < len(sent):
    rounds += 1
    missing = [p for p in sent if p["number"] not in have]
    for packet in deliver(missing):
        have[packet["number"]] = packet["text"]
    print(f"round {rounds}: asked for {len(missing):>2}, now hold {len(have)} of {len(sent)}")

print(f"\nafter {rounds} rounds:")
print("   " + "".join(have[n] for n in sorted(have)))
