# The merchant road is closed — 24 Oct, night

Concentrated liquidity was the trade's last and best hope: in v4 the same
capital in a narrow band earns several times the fees (≈6× at ±30%).

| band | holding through | **exiting when price leaves the band** |
|---|---|---|
| ±50% | −2.28% ± 0.80 | −1.82% ± 0.68 |
| ±30% | −3.43% ± 0.80 | −2.61% ± 0.54 |
| ±15% | −4.58% ± 0.82 | **−2.87% ± 0.41** |
| ±8% | −5.40% ± 0.83 | −2.50% ± 0.33 |

Calibration row: a ±99% band reproduces the full-range result already measured,
so the position formulas are sound.

## Two findings, one useful even though the road closes

**Concentration raises the median and destroys the mean.** At ±15% holding
through, the median is **+4.76%** and the mean **−4.58%**: the typical case is
good and the tail eats everything. Exiting on a range break cuts that tail —
the interval halves from ±0.82 to ±0.41 — which is a real technique worth
keeping.

**But the mean stays firmly negative at every width, and now the interval
excludes zero everywhere.** The reason is structural: concentrating liquidity
**amplifies adverse selection**. The tighter the band, the more reliably you are
filled with the coin exactly while it falls. The extra fees never pay for it.

## Verdict

Full range: break-even, not demonstrated, negative in the recent third.
Concentrated: clearly negative, tightly measured.
**No version of the merchant trade makes money on these pools.** Closed.

Roads closed tonight: the tail filter, tokenized equities, UniswapX (on
capacity), and the merchant itself. Remaining: leveraged tokens, measurable
only while New York is open.
