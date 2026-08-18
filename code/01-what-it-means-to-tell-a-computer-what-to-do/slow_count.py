"""Count once a second so the running program can be watched from outside.

Run it with: python3 slow_count.py
Stop it with control C.
"""

import os
import time

print(f"my process id is {os.getpid()}")

count = 0
while True:
    count += 1
    print(count)
    time.sleep(1)
