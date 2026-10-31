# The night the instrument was calibrated (20-21 Oct)

The founder refused to let the chain be closed on a sloppy audit. He was right, and the audit
found a real mistake — though not the one anyone expected.

## What the audit found first: we had measured 13% of the chain

Three days of work covered only the Pons memecoin corner. In one hour of chain, **64,842 swaps
across 2,056 pools, and only 2 of the 15 busiest pools are Pons**. Outside Pons the pools carry
real LP fees (0.30%, 0.05%, 1.00%) instead of Pons' zero, and 22 non-Pons pools even receive
`Donate` payments to liquidity providers — a mechanism Astra correctly insisted be checked
before verdict 5 could stand. (Checked: no Pons pool receives any. Verdict 5 stands, now
measured rather than assumed.)

Also corrected along the way: the first volume ranking summed `amount0/1e18` across all pools
and called it money. In a memecoin pool that figure is a token count, so coins with huge supply
looked like the chain's biggest markets. Ranking by **swap count** instead removed the illusion.

## Then the measurement outside Pons came back positive — twice

| | first 12h | previous 12h |
|---|---|---|
| Pons, median per pool | -0.82% | -0.93% |
| Pons, pools in profit | 10% | 5% |
| **non-Pons, median** | **+0.46%** | **+0.59%** |
| **non-Pons, pools in profit** | **70%** | **76%** |

Replicated on two non-overlapping windows, across ~1,000 pools each. For a few hours this was
the first replicated positive result of the project.

## The tell: the return equalled exactly twice the pool's fee

| pool fee | measured return |
|---|---|
| 1.00% | +1.96% |
| 1.10% | +1.72% |
| 0.30% | +0.49% |
| 0.06% | +0.20% |
| zero | -0.06% |

A regularity that clean is never a market edge. It is a piece of accounting counted backwards.
Verified on chain by cross-referencing swaps with token transfers: **when the PoolManager
*sends* tokens — i.e. the user is buying — `amount0` is NEGATIVE**. The code said `a0 > 0`
meant a buy. So the measurement bought at the low side and sold at the high side: the business
of the party who *collects* the spread, not the one who pays it.

## The calibration case, and why it is the real output of the night

After being fooled twice in opposite directions by the same sign, arguing about the third
number was pointless. So: build a case whose answer is known **before** measuring.

Buy and sell back immediately, entering at a buy print and exiting at the next sell print. No
time for the market to move. The result **must** be negative, roughly the pool's round trip.

| pool | instant round trip | expected |
|---|---|---|
| fee 1.00% | **-0.93%** | negative ✓ |
| fee 1.10% | **-1.42%** | negative ✓ |
| fee 0.35% | **-0.54%** | negative ✓ |
| fee 0.06% | -0.06% | negative ✓ |
| fee zero | +0.40% | ✗ |
| Pons | +0.42% | ✗ |

Fee-bearing pools pass, proportionally to their fee: **the instrument now measures**. Two rows
fail, and the calibration exists exactly to point at them.

The last one was settled by running the same trip **in both directions**, which cannot both
pay:

| pool | buy→sell | sell→buy |
|---|---|---|
| fee 1.00% | -0.90% | -2.37% |
| fee 1.10% | -1.16% | -2.22% |
| **Pons** | **+0.72%** | **+0.25%** |
| **fee zero** | **+0.36%** | **+0.40%** |

Both directions positive on the same pools. **The construction produces that number, not the
market.** The positive outside Pons is gone.

## One finding that survives, and makes the Pons verdicts worse

The Pons hook skims via `afterSwapReturnsDelta`, applied **after** the swap — so it never
appears in the `Swap` event amounts. Every Pons price series understates the cost by roughly
1% per leg. The Pons verdicts were not too harsh; they were too kind.

## What the night actually produced

Four spectacular numbers died in 24 hours: +172%, a +64.79% mean, a +20-point wallet edge, and
a replicated +0.5% across a thousand pools. Every one of them from an ordering, a join, or a
sign that picked the wrong case.

The output is not a strategy. It is a **calibrated instrument**: a measurement whose answer is
known in advance, which any future result has to pass before it is believed. That is worth more
than any of the four numbers would have been.

---

# The clean table, and the answer

A fourth defect had to be fixed before the table could be read: each horizon column kept only
the operations that *had* an exit at that distance, so +5 minutes showed +101% and +30 minutes
-0.68% — not two horizons, two populations. Now an operation enters the table only if it exists
at every horizon.

With all four corrections in place — verified sign, entry at a buy print and exit at a sell
print, permanent calibration row, common support across columns:

| pool group | calibration (instant) | +1 min | +5 min | +30 min |
|---|---|---|---|---|
| fee 1.00% | **-1.95%** ✓ | -1.83% | -1.62% | -1.61% |
| fee 1.10% | **-1.83%** ✓ | -1.62% | -1.91% | -2.10% |
| fee 0.35% | **-0.43%** ✓ | -0.36% | -0.34% | +0.00% |
| fee 0.06% | **-0.08%** ✓ | -0.07% | -0.06% | -0.05% |
| Pons | +0.36% ✗ | — | — | — |
| no fee | +0.44% ✗ | — | — | — |
| fee 0.01% | +0.01% ✗ | — | — | — |

**On every pool group whose calibration passes, following a buy returns approximately minus the
pool's toll, and it stays there at one minute, five minutes and thirty minutes.** There is no
drift to capture. The toll is paid at entry and nothing afterwards gives it back.

The rows whose calibration fails are the ones whose cost is invisible in the event data — Pons,
where the hook skims after the swap, and the zero-fee pools. Those are not evidence of profit;
they are evidence that the instrument cannot see their cost.

## The answer to the question

**On Robinhood Chain, with our one-second latency, taking liquidity does not pay — inside Pons
or outside it.** Seven positions measured, four spectacular false positives caught, and now a
table that states the result and proves its own validity in the first column.

What the project owns at the end of this night is not an edge. It is an instrument that can no
longer be fooled by the four errors that fooled it today, and a map of a chain measured to its
edges rather than to the edge of our patience.
