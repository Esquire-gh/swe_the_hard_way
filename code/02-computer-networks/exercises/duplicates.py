"""Exercise three: a network that sometimes delivers the same packet twice.

Nothing is lost here. Every packet arrives, and the message still comes out
wrong, because the receiver was only ever checking for gaps.

Run it with: python3 duplicates.py
"""

import random

MESSAGE = "a network does not deliver messages, it delivers packets"
SIZE = 8
random.seed(3)

sent = [{"to": "ada", "number": n, "text": MESSAGE[at:at + SIZE]}
        for n, at in enumerate(range(0, len(MESSAGE), SIZE))]

arrived = []
for packet in sent:
    arrived.append(packet)
    if random.random() < 0.4:        # a router forwarded it down two links
        arrived.append(packet)
random.shuffle(arrived)

missing = {p["number"] for p in sent} - {p["number"] for p in arrived}
print(f"packets sent:     {len(sent)}")
print(f"packets arrived:  {len(arrived)}")
print(f"the receiver's check for gaps says missing: {sorted(missing)}")

print("\nsorted by number:")
print("   " + "".join(p["text"] for p in sorted(arrived, key=lambda p: p["number"])))

kept = {p["number"]: p["text"] for p in arrived}
print("\nsorted by number, keeping each number once:")
print("   " + "".join(kept[n] for n in sorted(kept)))
