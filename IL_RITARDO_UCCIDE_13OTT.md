# Speed, not strategy, is the binding constraint

Half of all positions resolve within **6 seconds** (block time on this chain measured at
0.093s from our own data). Every earlier figure assumed we sell at the exact instant the
stop or target is touched - that is, that we are infinitely fast.

## What a realistic delay does

Exit taken at the first observed price at least N seconds after the touch:

| delay | 50-5 | stop -2% / 2x | stop -2% / 3x |
|---|---|---|---|
| instant | +7.82% | +8.49% | +5.49% |
| 1 second | +6.52% | +6.21% | +2.11% |
| 3 seconds | +6.42% | +5.86% | +2.35% |
| 10 seconds | +6.26% | +5.20% | +1.59% |
| 30 seconds | **+1.01%** | **+0.47%** | **-3.25%** |

At 30 seconds the edge is gone for every rule. Between 1 and 10 seconds it holds.

The 3x target is the most fragile: it loses more than half its return to a single second,
because its exits happen in the most violent moments.

**This moves the question.** It is no longer "does the strategy work" but "can we sell
within 10 seconds". Block time is 0.093s and direct calls to the curve contract are already
verified as possible, so 1-2 seconds should be reachable - but that must be measured, not
assumed.

## Second constraint: slots clog

With 500 EUR and 10 slots of 50 EUR, out of 724 opportunities only **139** can be taken -
585 pass while every slot is occupied.

24% of positions never resolve on their own: the curve simply stops trading, so the path
ends and the capital stays parked. Without a **time cut** those positions hold a slot
forever.

| policy | operations taken | capital after 45.6h |
|---|---|---|
| no time cut | 83 | 721 EUR |
| cut at 1 hour | 136 | **875 EUR** |
| cut at 15 min | 139 | 774 EUR |
| cut at 5 min | 139 | 749 EUR |

A one-hour cut is the best of the four: it frees slots without selling positions that are
still working.
