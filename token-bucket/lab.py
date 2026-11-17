# Token bucket: try it yourself (Rate Limiter, Part 2 · CS Motion)
# Press Run. Then change the two numbers below and run again.

CAPACITY = 10        # tokens the bucket holds = the biggest burst
REFILL_EVERY = 6.0   # seconds per new token = the rate (6 s -> 10 a minute)


class TokenBucket:
    def __init__(self, capacity, every):
        self.capacity, self.every = capacity, every
        self.tokens, self.last = float(capacity), 0.0    # starts full

    def allow(self, t):
        # Refill for the time that passed, never above capacity.
        self.tokens = min(self.capacity, self.tokens + (t - self.last) / self.every)
        self.last = t
        if self.tokens >= 1:
            self.tokens -= 1                             # spend a token: request passes
            return True
        return False                                     # empty: 429 Too Many Requests


def most_in(times, span):
    """Most requests in any `span` seconds."""
    return max((sum(1 for u in times if t <= u < t + span) for t in times), default=0)


# The bot from the video: 20 holds at 0:59.0-1:00.9, then one retry a second until 1:59.
bot = [59 + 0.1 * k for k in range(20)] + list(range(62, 120))

bucket = TokenBucket(CAPACITY, REFILL_EVERY)
passed = [t for t in bot if bucket.allow(t)]

print(f"Bucket: {CAPACITY} tokens, one new token every {REFILL_EVERY:g} s")
print(f"The bot sent {len(bot)} holds; {len(passed)} got through.")
print(f"Most in any 60 s: {most_in(passed, 60)}  (limit: 10 a minute)")
print(f"Most in any 2 s:  {most_in(passed, 2)}")
print()
print("Each second (# = a hold got through):")
for start, end, label in ((59, 90, "0:59"), (90, 120, "1:30")):
    print(label, "".join("#" if any(s <= t < s + 1 for t in passed) else "."
                         for s in range(start, end)))
