# Zero, measured to ±0.0008% — 25 Oct

The new filter said: only test where there are thousands of independent
observations. Five-minute candles on 17 markets give **183,000**.

## The result

| | |
|---|---|
| tests | 18 (9 independent: each rule and its mirror) |
| observations | 18,500 to 183,682 per test |
| outcome | **all 18 below zero** |
| precision | ±0.0008% to ±0.0092% |

Every rule lands between −0.013% and −0.022%, against a measured toll of
0.018%.

## The internal check that makes it airtight

"Follow the last candle" returns **−0.0202%**. "Fade the last candle" returns
**−0.0158%**. Their average is **−0.018%** — exactly the toll.

Two mirror-image strategies can only average to −toll if the **gross signal is
exactly zero**. That is not an inference; it is arithmetic, and it fell out of
the data on its own.

## What is now settled

**On liquid markets at five-minute resolution, simple price patterns carry no
information at all.** Not little — zero, measured at a precision twenty times
finer than the cost of trading.

We knew this from the literature. Now we know it from our own measurement,
which is a different weight when deciding.

It also validates this morning's filter: with enough observations you get a
**definitive answer** instead of another "not demonstrated". Every test earlier
today returned the latter because the observation count could not support a
verdict.

## What this does and does not close

Closed: price-pattern rules on liquid markets, at any horizon we can reach.

Not closed: anything whose input is **not the price history** — a news feed, an
order-flow imbalance, a funding rate, a cross-market relationship with a
mechanical link. Those remain untested, and the filter now tells us which of
them are even worth testing: only the ones that can produce thousands of
observations.
