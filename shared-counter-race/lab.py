# Two servers said yes: try it yourself (Rate Limiter, Part 3 · CS Motion)
# Press Run. Then change the numbers below and run again.

RATE = 500_000    # requests a second on the partner's key (the retry storm)
RTT_MS = 0.5      # one round trip from a gateway node to Redis, in ms
ATOMIC = False    # False: GET, compare, SET (2 trips) · True: one INCR (1 trip)
LIMIT = 2_000     # the partner may make 2,000 requests a second

import random
from collections import deque

# One second of requests arriving at random (seeded, so you get the video's numbers).
rnd, t, requests = random.Random(1), 0.0, []
while (t := t + rnd.expovariate(RATE)) < 1.0:
    requests.append(t)

rtt = RTT_MS / 1000
counter, allowed, log = 0, 0, []
pending = deque()                    # SETs still on their way: (time it lands, value)
for t in requests:
    read_at = t + rtt / 2            # the GET (or INCR) reaches Redis half a trip later
    while pending and pending[0][0] <= read_at:
        counter = pending.popleft()[1]    # a SET landed
    if ATOMIC:
        counter += 1                 # Redis adds and answers in one step: no gap
        ok = counter <= LIMIT
    else:
        seen = counter               # GET: the value right now...
        ok = seen < LIMIT
        if ok:                       # ...SET seen + 1 lands a round trip later
            pending.append((read_at + rtt, seen + 1))
    allowed += ok
    if len(log) < 4:
        log.append(f"  request {len(log) + 1}: Redis says {counter if ATOMIC else seen} -> "
                   + ("allowed" if ok else "429"))

print("One INCR" if ATOMIC else "GET, then SET")
print(f"{RATE:,} requests in one second, limit {LIMIT:,}")
print(f"Allowed: {allowed:,}   ({allowed / LIMIT:.1f}x the limit)")
print(f"Requests inside one round trip: {RATE * rtt:,.2f}")
print("The first four:")
print("\n".join(log))
