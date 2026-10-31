# The family, not six rules — 25 Oct

Nicolò's objection: *you closed price patterns after testing six rules.* Correct.
This is the test of the **class**.

Design: generate 28 mechanical rules systematically (rolling max/min/mean over
five windows, runs of 2–5 candles), × 2 directions × 2 horizons. For each, run
it **and** run the same number of entries at **shuffled times** on the same
market. Compare the two distributions. Cost excluded, so the statistic measures
signal and not how often a fixed cost fits inside the error. Only pairs
surviving in both cases are kept.

30 Binance markets, **477,180 hours**, 73 paired runs.

| | median t | 5% | 95% | extremes (|t|>2) |
|---|---|---|---|---|
| **real rules** | **−0.22** | −3.57 | +4.13 | **31** of 73 |
| shuffled entries | −0.08 | −2.38 | +2.63 | 13 of 73 |

## Two findings, the second worth more

**The centres coincide.** −0.22 against −0.08: the class of price-pattern rules,
taken whole, has **no directional edge**. This is no longer "six rules failed" —
it is a property of the family, measured over 73 paired combinations.

**The distribution is much wider.** Real rules reach −3.57 and +4.13 where
chance stops at −2.38 and +2.63, producing **31 extreme values against 13**.

That second line explains three months. A price rule does not predict
direction, but it does select moments **when something is happening**, so
outcomes scatter more. Which means that searching across a hundred rules finds
about **fifteen "significant" ones by construction** — twice what chance alone
would give.

We were not unlucky or shallow. **That family is a false-positive machine**, and
now the mechanism is measured rather than suspected.

## Register update

Families 1, 2 and 5 (price patterns, on any market, at any horizon) move from
**type B** (six rules tried) to **type A-** (the class measured: empty at the
centre, fat at the edges). Reopening them requires a reason beyond "we did not
try rule number seven".
