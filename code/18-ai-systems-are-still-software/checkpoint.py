# A training loop is a counter it holds in memory and a file it writes to
# disk now and then. Memory dies with the process; the file survives. When a
# run is killed, something restarts it (chapter fifteen's supervisor) and it
# resumes from the last file it wrote, repeating only the steps since then.
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CKPT = os.path.join(HERE, "checkpoint.txt")


def worker():
    step = 0
    try:
        with open(CKPT) as f:
            step = int(f.read())
    except FileNotFoundError:
        pass
    print("  resume from step %d" % step if step else "  start fresh")
    while step < 10:
        step += 1
        if step == 7 and "--crash" in sys.argv:
            print("  step 7: process killed, memory gone")
            sys.stdout.flush()
            os._exit(1)
        if step % 3 == 0:
            with open(CKPT, "w") as f:
                f.write(str(step))
            print("  step %d: checkpoint written to disk" % step)
        else:
            print("  step %d" % step)


if __name__ == "__main__":
    if "worker" in sys.argv:
        worker()
    else:
        if os.path.exists(CKPT):
            os.remove(CKPT)
        me = [sys.executable, os.path.abspath(__file__), "worker"]
        print("first run, it dies partway:")
        r1 = subprocess.run(me + ["--crash"], capture_output=True, text=True)
        print(r1.stdout, end="")
        print("supervisor restarts it:")
        r2 = subprocess.run(me, capture_output=True, text=True)
        print(r2.stdout, end="")
        os.remove(CKPT)
