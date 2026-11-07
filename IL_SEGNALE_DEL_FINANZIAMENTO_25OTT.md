# A signal with a perfect calibration row — 25 Oct

External information that is **not the price**: the funding rate on Hyperliquid
perps. Public, no key, hourly, across 178 markets. When funding is positive,
longs pay shorts — it measures where the crowd is, not where the price has been.

387,320 hourly funding readings and 135,038 hourly candles, same venue, so the
prices are the ones we would actually trade on.

## The calibration row is exact

Both directions of the same rule must average to −cost if there is no signal.

| horizon | against the crowd | with the crowd | average |
|---|---|---|---|
| 8h | −0.1429% ± 0.0431 | −0.0451% ± 0.0431 | **−0.094%** |
| 24h | −0.1932% ± 0.1259 | +0.0052% ± 0.1259 | **−0.094%** |
| 72h | −0.4561% ± 0.4093 | +0.2681% ± 0.4093 | **−0.094%** |

The declared cost is **0.094%**. Not approximately — exactly, at all three
horizons. The measurement is trustworthy, so what remains is real signal.

## The signal exists, and runs opposite to my hypothesis

I expected the crowd to be wrong. Separating gross from cost, **going against
the crowd loses**: −0.049% at 8h, −0.099% at 24h, **−0.362%** at 72h.

So the paying direction is **with the crowd**, and the edge **grows in order
with the horizon**: 0.05 → 0.10 → 0.36. Three horizons, same sign, scaling
magnitude. That is not the shape of noise.

(The accounting includes the funding cash flow itself, not only the price move:
going with the crowd means **paying** funding, and it still wins gross.)

## But the net is not demonstrated

With the crowd at 72h: **+0.268% ± 0.409**. The interval is too wide because
this used **24 of 178 available markets** and 1,377 non-overlapping
observations.

No new idea is needed — only **more markets**. With all of them the interval
narrows by roughly 2.5×, and that +0.268% either demonstrates or dies.
Download running.

---

## It did not survive the expansion — closed

112 markets instead of 24: **346,075 hours, 32,657 non-overlapping observations**
at 8h.

The calibration row stays exact at every horizon (both directions average to
−0.094%, the declared cost). The measurement is right. The gross signal is not:

| horizon | 24 markets | **112 markets** |
|---|---|---|
| 8h | +0.049% | **+0.003%** |
| 24h | +0.099% | **−0.037%** (sign flipped) |
| 72h | +0.362% | **+0.129%** |

The orderly progression 0.05 → 0.10 → 0.36, which impressed me precisely
because "that is not the shape of noise", became **0.00 → −0.04 → +0.13** with
five times the data. Inconsistent in sign.

**No net result is positive. Closed.**

### Why it fooled me, written down

The three horizons **share the same data**. They were never three independent
confirmations — they were three views of one small sample. **Coherence across
horizons is not evidence when the horizons are nested in the same observations.**
Independent confirmation requires different markets or different periods, not
different exit times on the same entries.

### What stands

The calibration row returned the exact declared cost in **six** separate
measurements across two samples. The instrument is reliable — so when it does
find something, there will be no doubt that it is real.
