"""Exercise two: three times four on the machine from machine.py.

Only set, add, jump_if, show and stop exist, so multiplying means adding
four to a running total three times. Fifteen steps.

Run it with: python3 times.py
"""

memory = [0] * 8

program = [
    ("set", 0, 3),        # box 0: how many times round to go
    ("set", 1, -1),       # box 1: what we add to the counter each time
    ("set", 2, 0),        # box 2: the running total
    ("set", 3, 4),        # box 3: what we add to the total each time
    ("add", 2, 3),        # total = total + 4
    ("add", 0, 1),        # one fewer time to go
    ("jump_if", 0, 4),    # not finished? go back to instruction 4
    ("show", 2),
    ("stop",),
]

counter = 0
step = 0

while True:
    instruction = program[counter]
    name = instruction[0]
    step += 1
    print(f"step {step:>2}   counter={counter}   {name:<8} memory={memory[:4]}")

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
