"""Keep a process running, with a health check that is not fooled.

A supervisor restarts a process when it dies. That alone is not enough: a
program that crashes the instant it starts gets restarted forever and,
from a distance, looks exactly like one that is running. So the supervisor
also asks the process whether it actually works, on the address the
process answers only when it does. This runs a healthy server, then a
crashing one, and tells them apart.

Run it with:  python3 supervisor.py
"""

import http.client
import subprocess
import sys
import time

HERE = __file__.rsplit("/", 1)[0]


def healthy():
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8210, timeout=0.5)
        conn.request("GET", "/health")
        ok = conn.getresponse().status == 200
        conn.close()
        return ok
    except OSError:
        return False


def supervise(args, label, rounds=4):
    print(label)
    restarts = 0
    for _ in range(rounds):
        child = subprocess.Popen(
            [sys.executable, f"{HERE}/flaky_server.py", *args],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.4)
        alive = child.poll() is None
        good = healthy() if alive else False
        mark = "ok" if good else "FAIL"
        print(f"    started, alive={alive}, health={mark}")
        if good:
            print("    it works; the supervisor leaves it up")
            child.terminate()
            child.wait()
            return
        child.terminate()
        child.wait()
        restarts += 1
    print(f"    restarted {restarts} times, never healthy: a crash loop")


supervise([], "watching a healthy server:")
print()
supervise(["crash"], "watching a server that crashes on startup:")
