# The +18.9% is withdrawn — 23 Oct

The last surviving strategy — buy every graduated coin at the end of minute one,
sell at 2x — was carried for weeks on a result of **+18.9% over 334 coins,
confirmed out of sample**. Measured on the full archive it is **−4.5% ± 2.3 over
5,139 coins**. The interval does not contain zero.

## It is not the rule, it is the sample

Seven fully-specified variants, to find which undeclared choice produced the +18.9%:

| variant | mean |
|---|---|
| 24h deadline, exit only on a sell print | −4.5% ± 2.3 |
| 2x counted on any print | −4.1% ± 2.3 |
| no deadline, hold while data lasts | −4.5% ± 2.3 |
| no deadline + 2x on any print | −4.1% ± 2.3 |
| stuck positions dropped instead of −100% | −4.5% ± 2.3 |
| ≥50 trades only | −4.3% ± 2.3 |
| ≥50 trades + 2x on any print | −3.9% ± 2.3 |

All seven agree. **334 coins were 6% of 5,139** — a sample of what we had
collected, not of the market. The lesson was already written in September and
was not applied here.

## Two further facts, either of which was fatal on its own

- **Peak simultaneous positions: 87.** At EUR 50 a ticket the strategy needs
  EUR 4,350. An average per coin describes an account we do not have.
- A EUR 52 ledger, one position at a time, all-in: 52 → 244 → **0.70**.
  All-in sizing on a negative-median bet is ruin by construction, not bad luck.

## Status

No strategy survives on any of the three chains. What survives is the
instrument: verified trade sign, entry on a buy print and exit on a sell print,
a permanent calibration row, common support, stuck positions at −100%, follow
the money until it stops, independence measured by co-activity.

Every positive result this project produced was destroyed by that instrument.
That is what it was built to do.

---

## Addendum, same day: the calibration row caught a wrong sign

The −4.5% above rested on a **declared** 6% toll. Measuring it instead of
assuming it, the instant round trip came out **positive** (+1.01% mean at zero
blocks) — which rule 3 says makes the row unreadable, so the verdict was
suspended rather than kept.

Measuring both directions at the same block resolved it:

| direction | n | mean |
|---|---|---|
| "buy" print → "sell" print | 28,523 | **+0.72%** |
| "sell" print → "buy" print | 31,611 | **−1.01%** |

Opposite signs of similar size: that is the **spread**, and the profitable
direction is the one that collects it. So in the post-diploma archive the labels
are inverted relative to the curve data: `a0 < 0` is a **sell** (the bid), not a
buy. The 21 Oct on-chain verification holds for the curve, and was wrongly
carried over to PoolManager swaps.

Re-running with the correct side and the measured spread instead of the declared
6%:

| labelling | mean | median |
|---|---|---|
| old (entering on the favourable side) | −0.4% ± 2.4 | −21.1% |
| **correct** | **−5.0% ± 2.4** | **−40.1%** |

The verdict stands and is worse, now on a measured basis. Note that under the old
labelling the result was indistinguishable from zero: **entering on the right
side of the book was worth almost five points** — the whole distance between
"maybe" and "no".
