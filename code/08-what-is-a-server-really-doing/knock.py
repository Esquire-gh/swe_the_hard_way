"""Wake up whichever waiter is running in the other window.

Run it with: python3 knock.py file
         or: python3 knock.py pipe
"""

import pathlib
import sys

HERE = pathlib.Path(__file__).parent
WHICH = sys.argv[1] if len(sys.argv) > 1 else "file"

if WHICH == "pipe":
    # Opening a pipe for writing waits until somebody is reading it.
    with open(HERE / "knock.pipe", "w") as pipe:
        pipe.write("hello from the other window\n")
    print("wrote into the pipe")
else:
    (HERE / "knock.txt").write_text("hello from the other window\n")
    print("wrote the file")
