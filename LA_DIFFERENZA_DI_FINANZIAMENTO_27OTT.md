# The funding spread between two venues — real, and far too small — 27 Oct

Long on one exchange, short on the other, same coin. The two prices track
within 0.045% (measured earlier today), so there is no price risk worth the
name. What is collected is the **difference in funding rate** between the two
venues. 39 coins, 500 Binance payments each, Hyperliquid hourly summed into
8-hour windows to match.

Direction is chosen on the **previously observed** difference, never on the
one being collected — the look-ahead that destroyed the arbitrage result an
hour earlier.

## Result, with all three ingredients

Funding collected, plus the change in the price spread while holding (which is
not zero and is realised at the close), minus 0.19% of four legs.

| hold | net | gross (net + 0.19%) |
|---|---|---|
| 8 hours | −0.1849% ± 0.0004 | +0.0051% |
| 24 hours | −0.1762% ± 0.0014 | +0.0138% |
| 72 hours | −0.1578% ± 0.0054 | +0.0322% |
| 168 hours | −0.1138% ± 0.0223 | **+0.0762% ± 0.0223** |

**This is the first gross in weeks that survives the entry delay.** It is real,
it is delta-neutral, and at seven days the interval does not touch zero.

Annualised: ~4% per year gross. Margin is required on **both** venues, so the
capital actually tied up is double — call it **~2% per year on deployed
capital**. The 0.19% entry toll pays for itself in about 18 days and is then
irrelevant, since the position can simply be held.

## Why it is still closed

It is a **yield**, and a yield multiplies by capital.

| capital | per year |
|---|---|
| €52 | **~€1** |
| €5,000 | ~€100 |
| €50,000 | ~€1,000 |

This is the "locked capital" architecture, already closed with numbers weeks
ago, and it closes again for the same reason: it pays in proportion to money
we do not have. Nothing about it is wrong — it is simply not a machine, it is
an interest rate.

Worth recording precisely rather than discarding: if capital ever arrives, this
is a measured, delta-neutral place to put it, and the measurement is done.

---

## The ceiling, measured — same day

Would it pay better to take only the large spreads? The toll is one-off and
amortised by holding, so a rarer but fatter spread would raise the rate.

| trigger per 8h window | positions | net over 7 days | gross, annualised |
|---|---|---|---|
| none | 248 | −0.1215% ± 0.0201 | +3.6% |
| 0.02% | 91 | −0.0806% ± 0.0425 | **+5.7%** |
| 0.05% and above | too few to measure | — | — |

**The tail is thin.** Between these two venues the funding difference almost
never exceeds 0.05% in an 8-hour window, so selection buys very little: the
ceiling of the whole architecture is roughly **6% per year**, not more.

That closes the question properly. It is an interest rate with a known roof,
not a machine — and at €52 of capital the roof is about €1.50 a year.

---

## Audit — 27 Oct, evening: the clustering correction, propagated here

The calendar test that evening exposed a systematic flaw: pooling
observations across markets as if independent, when markets move together.
Every result of the day was computed that way, so every interval was
potentially too narrow. The correction was propagated to this result first,
because it was the only positive one left standing.

Collapsing to the **opening date** (average across coins within a date, then
statistics across dates):

| counting | observations | gross over 7 days |
|---|---|---|
| as I had it (coin-date) | 243 | +0.0762% ± 0.0223 |
| **correct unit (the date)** | **25** | **+0.1034% ± 0.0362** |

**It survives: +5.4% per year, interval still clear of zero.** The first time
today an audit confirmed a result instead of destroying one.

## Why no other verdict can change

Correcting for clustering can only **widen** intervals, so it can only move a
result from "demonstrated" to "not demonstrated", never the reverse. Every
other road today ended either at zero gross or as "not demonstrated" already.
This was the only demonstrated positive, and it held.

## The honest caveat

**25 independent observations**, not 243. The rate is real at the sizes
measured, and it remains what it was: an interest rate of about 5% per year,
worth roughly **€1 a year on €52**.

---

## Deeper history — the estimate falls

The first downloader stopped at 500 funding payments per coin (166 days) on a
faulty loop exit. Fixed, it walks back **2,470 days** — nearly seven years.

| history | independent observations | gross over 7 days | annualised |
|---|---|---|---|
| 166 days | 25 | +0.1034% ± 0.0362 | **+5.4%** |
| **2,470 days (capped by Hyperliquid)** | 28 | **+0.0612% ± 0.0312** | **+3.2%** |

Still demonstrated — the interval clears zero — but **the number falls by
40% when measured over more time**. That is the fourth estimate today to
shrink when given more data, always in the same direction, and it is a
warning not to treat +3.2% as a floor either.

Independent observations barely moved (25 → 28) because the binding
constraint was never Binance: it is my **Hyperliquid archive, 291 days**.
More history on one venue does not lengthen the overlap. Extending the
Hyperliquid side is the only way to measure this more precisely — and at
€1.66 a year on €52, there is no hurry.
