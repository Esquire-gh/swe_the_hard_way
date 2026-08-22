"""Exercise two: what the polling interval buys and what it costs.

Sweep the gap between looks. For each setting, wait for a message that
arrives at a moment the waiter cannot predict, and record two numbers:
the processor time spent looking, and how long the message sat there
before it was noticed.

Run it with: python3 sweep.py
"""

import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).parent
FLAG = HERE / "sweep.flag"
GAPS = (0.001, 0.005, 0.050, 0.200)
TRIES = 5
DELAY = 0.4                      # how long the writer waits before knocking

WRITER = (
    "import pathlib, sys, time;"
    "time.sleep(float(sys.argv[2]));"
    "pathlib.Path(sys.argv[1]).write_text(repr(time.time()))"
)

print(f"{'gap':>8}  {'looks':>7}  {'processor time':>14}  {'noticed late by':>15}")

for gap in GAPS:
    looks = late = cpu = 0.0
    for _ in range(TRIES):
        FLAG.unlink(missing_ok=True)
        writer = subprocess.Popen([sys.executable, "-c", WRITER,
                                   str(FLAG), str(DELAY)])
        started = time.process_time()
        while not FLAG.exists():
            looks += 1
            time.sleep(gap)
        noticed = time.time()
        cpu += time.process_time() - started
        late += noticed - float(FLAG.read_text())
        writer.wait()

    print(f"{gap * 1000:>6.0f}ms  {looks / TRIES:>7.0f}  "
          f"{cpu / TRIES:>13.4f}s  {late / TRIES * 1000:>14.1f}ms")

FLAG.unlink(missing_ok=True)
