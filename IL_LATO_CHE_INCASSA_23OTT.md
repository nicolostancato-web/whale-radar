# The side that collects — 23 Oct

Grok's sentence, which is the most useful thing produced in three months:

> *"The calibration row has been showing you the money the whole time, and it
> was filed as a fuse."*

Every table that came out "minus the toll, then flat" was followed by another
taker rule. But **someone receives that toll**, and we never once asked who.

## The new process rule, adopted

A taker table that dies on the toll may **not** be followed by another buying
rule. It must be followed by a **recipient ledger** for that toll — hook,
locker, protocol, creator, Donate claimant, in-range LP — and a recipient
enters the queue only if an arbitrary caller can become that address.

## What the first recipient ledger found

| measurement | result |
|---|---|
| liquidity moves, 3 min | 1,011 across 66 pools |
| distinct payers | 63, top three only 36% — not a cartel |
| positions opened and closed in the same block | **0** |
| Donate returned to LPs vs gas spent moving liquidity | **0.11×** — the Donate channel is dead |
| pools with **no hook at all** | **65 of 143** — plain v4, the fee goes entirely to LPs |
| declared fees on active pools | 0.01%, 0.30%, **1.00%** |

Gross fee yield over a 30-minute window, computed from the Swap event's own
liquidity and price fields (fees = fee% × native volume; active capital =
2L/√P):

| pool | swaps | fee | active capital | **gross yield / 30 min** |
|---|---|---|---|---|
| 0xb2cf3cbf… | 222 | 1.00% | 13.4 | **3.38%** |
| 0xbc8ce98d… | 228 | 1.00% | 11.8 | **3.33%** |
| 0x57f029ac… | 1002 | 0.30% | 30.9 | **1.29%** |

## What this does and does not establish

It does **not** establish profit. It is gross: it excludes the loss from holding
the coin as it falls, which on a memecoin is not impermanent but permanent.

It does establish something we have never had: a gross of **several points in
thirty minutes**, roughly ten times the toll that killed all eight previous
strategies. For the first time the net has room to survive.

Also corrected today, by Grok: a 4.7-second position life on a 100 ms chain is
~50 blocks and is the signature of a maker **recentring** a range, not closing
a trade. Scoring each add/remove as its own trade hides the inventory.

## Next, in order

1. Value of the native token, so "13.4 active capital" becomes euros and we know
   what share EUR 52 buys.
2. Simulate one LP position over a pool's whole life: fees collected versus
   terminal composition, valued at the last sell print, stuck inventory at −100%.
3. Calibration row for this table: an entity whose positions saw zero swaps must
   come out negative by the gas.
