"""A machine that does one thing at a time, and nothing else.

Run it with: python3 machine.py
"""

# Eight numbered boxes. This is the whole memory of this machine, and the
# printing below shows the first two, which are the only ones this program uses.
memory = [0] * 8

# The program. Every line is one instruction, and there are six of them.
program = [
    ("set", 0, 3),       # box 0 holds the number we are counting down
    ("set", 1, -1),      # box 1 holds the amount we add each time
    ("show", 0),
    ("add", 0, 1),
    ("jump_if", 0, 2),   # if box 0 is not zero, go back to instruction 2
    ("stop",),
]

counter = 0   # the number of the instruction that comes next
step = 0

while True:
    instruction = program[counter]
    name = instruction[0]
    step += 1
    print(f"step {step:>2}   counter={counter}   {name:<8} memory={memory[:2]}")

    if name == "set":
        memory[instruction[1]] = instruction[2]
        counter += 1
    elif name == "add":
        memory[instruction[1]] += memory[instruction[2]]
        counter += 1
    elif name == "show":
        print(f"                        output: {memory[instruction[1]]}")
        counter += 1
    elif name == "jump_if":
        counter = instruction[2] if memory[instruction[1]] != 0 else counter + 1
    elif name == "stop":
        break
