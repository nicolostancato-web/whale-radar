# Mechanically-linked pairs: closed, and a methodological catch — 25 Oct

Gasoline is refined from crude; so is heating oil. Gold and silver are both
safe-haven metals. Where two things are bound by a real constraint, the spread
between them ought to revert — not because of a pattern, but because of the
physics of the economy.

The idea passes every filter we have: long-short (no tide), it uses the
**relationship** rather than one price's history (so it is not closed by this
morning's result), and five-minute data gives tens of thousands of observations.

## First run: three results above zero — all artefacts

At the 3-hour horizon: heating-oil/crude **+0.1304% ± 0.0562**,
gasoline/heating-oil **+0.1034% ± 0.0863**, soy/corn **+0.0358% ± 0.0277**.

**The intervals were false.** At a 36-candle horizon, signals firing on
consecutive candles share 35 of 36 periods. I computed the interval as if the
observations were independent. The effective sample was not 2,094 but about 58.

## Second run: only non-overlapping observations

Every positive disappeared:

| | before (overlapping) | after (non-overlapping) |
|---|---|---|
| gasoline/heating-oil, 36 | +0.1034% ± 0.0863 **above zero** | +0.0862% ± 0.2496 **not demonstrated** |
| heating-oil/crude, 36 | +0.1304% ± 0.0562 **above zero** | drops out entirely |
| soy/corn, 36 | +0.0358% ± 0.0277 **above zero** | +0.0681% ± 0.0826 **not demonstrated** |

Short horizons remain clearly negative — the toll. Longer horizons demonstrate
nothing. **Closed.**

## The lesson, which is general

> **When observations overlap, the interval is wrong by a factor of √horizon.**

At 36 candles it is six times too narrow — easily enough to turn noise into a
discovery. From now on overlapping observations do not enter a calculation.

## The day's tally

Built a generic machine for any market. Closed price patterns to a precision of
**±0.0008%**. Closed cross-sectional ranking. Closed mechanically-linked pairs.
Derived two new filters: count the observations **before** testing, and never
overlap them.

No method found. But three whole families of strategy eliminated permanently,
in a day rather than a quarter.
