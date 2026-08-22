"""Why a queued job must be safe to do twice.

A worker can die after taking a job and before finishing it. If the queue
forgot the job the moment it handed it over, that work is lost, so a real
queue keeps the job until the worker reports success and gives it to
somebody else if that never comes. The price is that a job can run twice.
This shows it: a worker takes a job, is killed mid-way, and a second
worker picks the same job up and runs it again.

Run it with:  python3 at_least_once.py
"""

# The "queue" is a list of jobs, each not removed until it is acknowledged.
queue = [{"id": 1, "task": "email ada@example.com"}]
acknowledged = set()
side_effects = []          # every real action the workers actually took


def take():
    """Hand out the first unacknowledged job, but do not remove it yet."""
    for job in queue:
        if job["id"] not in acknowledged:
            return job
    return None


def do(job, die_before_ack):
    side_effects.append(job["task"])        # the real action happens here
    if die_before_ack:
        return                              # killed here: never acknowledged
    acknowledged.add(job["id"])             # only now is the job finished


first = take()
print(f"worker A takes job {first['id']} and is killed mid-way")
do(first, die_before_ack=True)

second = take()               # the same job is still unacknowledged
print(f"worker B takes job {second['id']}, the same one, and finishes it")
do(second, die_before_ack=False)

ran = side_effects.count("email ada@example.com")
print(f"\nthe job ran {ran} times")
print(f"actions taken: {side_effects}")
print("the email was sent twice: this is why queued work must be idempotent")
