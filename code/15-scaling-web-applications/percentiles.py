"""Why the average request time hides the visitor who is suffering.

A hundred requests: ninety are fast and ten are slow. The average sits
between the two and describes neither. The median looks wonderful. The
number that catches the slow tenth is the percentile: the time that
ninety five per cent of requests came in under.

Run it with:  python3 percentiles.py
"""

times_ms = [10] * 90 + [500] * 10      # ninety fast, ten slow


def percentile(values, which):
    ordered = sorted(values)
    spot = (len(ordered) - 1) * which / 100
    return ordered[round(spot)]


mean = sum(times_ms) / len(times_ms)
print(f"requests measured:   {len(times_ms)}")
print(f"mean:                {mean:7.1f} ms   (looks healthy)")
print(f"p50 (the median):    {percentile(times_ms, 50):7.1f} ms")
p95 = percentile(times_ms, 95)
print(f"p95:                 {p95:7.1f} ms   (the slow tenth)")
