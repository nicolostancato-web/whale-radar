# Eleventh road: UniswapX exists, but the whole pie is EUR 40 a day — 24 Oct

UniswapX **is** live on Robinhood Chain: **428 fills in 10.3 hours** (~1,000 a
day), **20 distinct solvers**, the largest taking only 35%. Not a closed garden,
which is more than can be said for most of what we have looked at.

## The measurement, and the defect it exposed first

Counting only ERC20 flows gave **0 of 42 fills positive**. A solver losing on
every fill would stop: that is a defect report, not a finding. The missing leg
is **native ETH, which emits no Transfer event** — so the solver's outgoings
were visible and their income was not.

With the native balance delta included the shape becomes plausible: median
0.0000, mean **+EUR 0.04** per fill, 1 of 3 positive. (n=3. The RPC keeps
historical state for only ~8 minutes, so the sample can only be built a few
fills per pass; a collector now runs each cycle.)

## Capacity first, as the rule now requires

~1,000 fills a day × EUR 0.04 = **EUR 40 a day for the entire chain**, split
among 20 solvers with faster machines than ours. Our realistic share: **EUR 2 a
day**. Taking literally everything: EUR 40.

**Even if the sign proves positive, this is a tip, not a machine.** Said now
rather than after three days of collection, because the capacity decides it and
capacity needed only a multiplication.

The collector stays on — it costs nothing — but the answer is not here.

## Twelfth road, parked an hour ago, with the firmest mechanism yet

`AAPLx3L/USDG`, 3,062 swaps: a **3× leveraged Apple token**. Leveraged products
rebalance daily and decay structurally, independently of where the underlying
goes. Not a pattern — an accounting identity.
