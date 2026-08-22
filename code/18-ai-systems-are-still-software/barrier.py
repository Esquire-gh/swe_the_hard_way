# Distributed training combines every machine's work at the end of each step,
# and no machine can start the next step until all of them arrive. A barrier
# is that meeting point. One slow machine makes every other machine wait, so
# the slowest sets the pace: being slow is worse than being dead, because a
# dead one is noticed and replaced while a slow one just holds the line.
import threading
import time

N = 4
STEPS = 3
barrier = threading.Barrier(N)
waited = [0.0] * N


def worker(i):
    slow = i == 0
    for _ in range(STEPS):
        time.sleep(0.30 if slow else 0.05)   # this machine's share of the work
        start = time.perf_counter()
        barrier.wait()                        # combine before the next step
        waited[i] += time.perf_counter() - start


start = time.perf_counter()
threads = [threading.Thread(target=worker, args=(i,)) for i in range(N)]
for t in threads:
    t.start()
for t in threads:
    t.join()
total = time.perf_counter() - start

print("%d workers, %d steps, worker 0 is slow: %.2fs total" % (N, STEPS, total))
for i in range(N):
    print("  worker %d (%s) waited %.2fs at the barrier"
          % (i, "slow" if i == 0 else "fast", waited[i]))
