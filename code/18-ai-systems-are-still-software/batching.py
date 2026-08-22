# The expensive hardware runs one forward pass at a time, and a pass costs
# about the same whether it carries one request or many. So the server waits
# a moment to collect a batch and runs them together: chapter fifteen's queue
# with an intentional delay, trading a little latency for a lot of throughput.
# Letting a new request join a batch already running is continuous batching.
import time

BATCH = 8
PASS = 0.10          # one forward pass, the same cost for 1 request or BATCH
REQUESTS = 64


def one_at_a_time(n):
    start = time.perf_counter()
    for _ in range(n):
        time.sleep(PASS)            # a whole pass carrying a single request
    return time.perf_counter() - start


def batched(n):
    start = time.perf_counter()
    for _ in range((n + BATCH - 1) // BATCH):
        time.sleep(PASS)            # a whole pass carrying up to BATCH at once
    return time.perf_counter() - start


a = one_at_a_time(REQUESTS)
b = batched(REQUESTS)
print("%d requests, one forward pass costs %.2fs either way" % (REQUESTS, PASS))
print("  one at a time:    %.2fs   (%2.0f req/second)" % (a, REQUESTS / a))
print("  in batches of %d:  %.2fs   (%2.0f req/second)"
      % (BATCH, b, REQUESTS / b))
print("  same hardware, throughput up %.0fx by filling a batch" % (a / b))
