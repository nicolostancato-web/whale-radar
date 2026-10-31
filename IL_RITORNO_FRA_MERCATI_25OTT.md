# Cross-market reversal: a real gross signal that two legs of cost eat — 25 Oct

The one family whose selector is **not** taken from the market's own candle:
rank 60 Binance perps by trailing return, buy the laggards, sell the leaders,
rebalance hourly. Long-short, so no tide. At hourly frequency the cycle count
is thousands, which is what made the monthly version undecidable this morning.

## Gross: the signal is real

The five strongest combinations all point the **same way** — reversal — with
t from +2.11 to **+3.63** and gross returns of +0.03% to **+0.1156%** per cycle.
Unlike the other families, the extremes are not scattered in both directions.

## Net: it dies

With the two legs of cost (0.10% per cycle) included, and split by markets
(odd/even) and by period:

| combination | all | markets A | markets B | period 1 | period 2 |
|---|---|---|---|---|---|
| 72h → 4h | −0.047% | −0.033% | −0.068% | −0.034% | −0.061% |
| 12h → 4h | −0.056% | −0.033% | −0.081% | −0.045% | −0.094% |
| **72h → 12h** | **+0.016%** | **+0.042%** | **−0.030%** | **+0.064%** | **−0.027%** |
| 24h → 4h | −0.061% | −0.049% | −0.063% | −0.065% | −0.059% |
| 168h → 12h | −0.057% | −0.054% | −0.033% | −0.029% | −0.044% |

The only combination with positive cells is inconsistent across every split —
positive on markets A and period 1, negative on markets B and period 2. That is
the signature of noise, not of an effect.

## A correction to my own earlier reading

In the two previous class tests I said "the medians coincide at zero, so no
directional edge". **That was an identity, not evidence**: including both
mirror directions on the same entries forces the median to zero, in the real
set and the shuffled set alike. The valid part of those tests was the
comparison of **spread**, not of centre. An edge shows as **asymmetry between
the mirrors** — which is exactly what appeared here, and then died on cost.

## The invariant, ninth time

Gross exists, gross is small, the toll eats it.

What has moved: at the start the toll was 6% against a gross of 1.5% — a factor
of four apart. Now the toll is 0.10% and the gross 0.12%. **They have nearly
touched.** Not enough, but the problem is finally a matter of hundredths rather
than orders of magnitude.

---

## It replicates across venues — and it is gone in the recent period

With **maker** costs the Binance result is 5 of 5 cells positive (one
demonstrated). Tested unchanged on **Hyperliquid** — different venue, different
markets, different history:

| | all | markets A | markets B | period 1 | period 2 |
|---|---|---|---|---|---|
| Binance (maker 0.04%) | +0.076% | +0.102% | +0.030% | **+0.124%** | +0.033% |
| Hyperliquid (maker 0.03%) | +0.098% | +0.082% | +0.079% | **+0.181%** ✓ | +0.004% |

**It replicates.** The attention candidate, under this exact check, reversed
sign. This one does not — the first thing in the whole search to survive a
change of venue.

## But the recent half is zero on both, and that is one observation, not two

Both datasets **end today**, so the two "second halves" are the **same calendar
window** — roughly mid-2026 to October. They are not two independent decays
confirming each other; they are one window seen twice.

**Honest reading: the effect was there and is not there now.** Competed away, or
a regime change. For trading only the present matters, and the present reads
zero.

## Two caveats that would have to be answered anyway

1. **Maker fills are assumed, not measured.** The whole positive margin lives in
   the difference between paying 0.10% and paying 0.04%. A maker is not always
   filled, and is filled more often when wrong. That adverse selection is not in
   these numbers and could exceed the margin entirely.
2. At taker cost the Hyperliquid recent half is **−0.056%**.

Filed as: **replicated, not tradeable now.** The only candidate ever to survive
a venue change, and it survived into a period where it does not pay.

---

## Quarter by quarter: weaker than my own script's label

| quarter | net per cycle |
|---|---|
| 2025-Q1 | **+0.250%** |
| 2025-Q2 | +0.131% |
| 2025-Q3 | +0.086% |
| 2025-Q4 | +0.019% |
| 2026-Q1 | +0.125% |
| 2026-Q2 | −0.075% |
| 2026-Q3 | +0.028% |
| 2026-Q4 | −0.017% |

Slope −0.033% per quarter, and the script printed "orderly decline" — but **I
chose that threshold arbitrarily**, which is exactly the thing I have forbidden
myself. Reading the numbers instead of the label: the decline is **not
monotone** (2026-Q1 rises again), and **no quarter is individually
demonstrated** — every value sits inside its own interval.

So the correct reading is soberer than an hour ago: the whole effect rests on
**pooling** the quarters, the first is the largest, and the last four hover
around zero. Compatible with decay; equally compatible with one lucky quarter
followed by nothing.

## Final state of the candidate

- **Replicates across two venues** — the only thing in three months that does.
- **No quarter stands on its own.**
- **The recent period is zero** on both venues.
- **The entire margin depends on maker fills**, which were assumed, never
  measured, and are adversely selected by construction.

**Not tradeable, and the evidence is thinner than it looked this evening.**
