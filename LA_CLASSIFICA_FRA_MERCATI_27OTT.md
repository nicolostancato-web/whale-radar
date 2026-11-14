# Ranking across markets — the tide cancels, and so does the edge — 27 Oct

Every test today asked *when* to buy one market, and drowned in the tide —
t-statistics of −5 and −10 are the market falling, not a signal. A
cross-sectional test asks *which of 300*, buying the top decile and selling
the bottom: **the common movement cancels by construction.**

This family was rejected before, but on 18 commodities and 99 equities, where
865 cycles meant 70 years. With 318 crypto perpetuals and hourly data the
power objection no longer applies: **15,919 hours with at least 60 markets
present.**

## The design validated itself

The control assigns markets to the two sides **at random** on the same dates.
It returns **−0.20% to −0.32%** — the toll, and nothing else, which is exactly
what a correct implementation must produce. The code is not manufacturing
signal.

## The result

| lookback | hold | cycles | net | |
|---|---|---|---|---|
| 12h | 12h | 1,325 | −0.1963% ± 0.1309 | below zero |
| 24h | 12h | 1,324 | −0.2688% ± 0.1298 | below zero |
| 72h | 24h | 660 | −0.2831% ± 0.2704 | below zero |
| 168h | 12h | 1,312 | −0.2080% ± 0.1398 | below zero |
| 12h | **72h** | 220 | +0.1343% ± 0.7950 | — |
| 24h | **72h** | 220 | +0.0344% ± 0.8233 | — |
| 72h | **72h** | 220 | +0.2173% ± 0.7358 | — |
| 168h | **72h** | 218 | +0.2000% ± 0.9339 | — |

At 12 and 24 hours of holding the net is negative and equal to the toll:
**gross zero**, the tenth time today.

At 72 hours all four cells are positive with the control negative — but the
interval is **±0.8**, which is fog containing zero, and the four cells share
the same periods so they are not four pieces of evidence.

## Why it closes, with the number

To shrink ±0.8 enough to resolve a +0.2% effect needs the interval four times
tighter, so **sixteen times the cycles**: ~3,520 cycles × 72 hours ≈
**29 years** of common history across 300 markets. The data does not exist and
will not for decades.

This is not "we found nothing". It is **not measurable with the data that
exists** — the same verdict as the commodities ranking, reached again from the
other side after removing the objection that killed it the first time.
