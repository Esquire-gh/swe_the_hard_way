"""Wait for a message by asking over and over, and count what that costs.

Run it with:            python3 polling.py
Then in another window: python3 knock.py file
"""

import pathlib
import time

MESSAGE = pathlib.Path(__file__).parent / "knock.txt"
MESSAGE.unlink(missing_ok=True)

print("watching for knock.txt")
looks = 0
wall_started = time.perf_counter()
cpu_started = time.process_time()

while not MESSAGE.exists():
    looks += 1
    time.sleep(0.005)

wall = time.perf_counter() - wall_started
cpu = time.process_time() - cpu_started

print(f"message: {MESSAGE.read_text().strip()!r}")
print(f"waited {wall:.1f} seconds of wall clock")
print(f"looked {looks} times, and found nothing {looks - 1} of them")
print(f"spent {cpu:.3f} seconds of processor time doing it")
MESSAGE.unlink()
