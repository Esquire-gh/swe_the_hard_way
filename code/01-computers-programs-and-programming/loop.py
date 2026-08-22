# Four lines with a loop in them, for taking apart with dis.
#
# Run it with:      python3 loop.py
# Disassemble with: python3 -m dis loop.py

total = 0
for n in range(3):
    total = total + n
print(total)
