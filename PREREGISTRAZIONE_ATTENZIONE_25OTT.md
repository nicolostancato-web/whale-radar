# Pre-registration — fading the attention spike — 25 Oct, before the split test

## The candidate, fixed now

- **Universe**: Hyperliquid perps, hourly candles.
- **Signal**: the hour's volume (or trade count) exceeds the **95th percentile**
  of that market's previous 500 hours.
- **Direction**: **fade** the hour's own move — if the hour closed up, go short;
  if down, go long.
- **Exit**: exactly **4 hours** later.
- **Cost**: 0.094% per round trip (taker, both legs).
- **Observations**: non-overlapping only.
- **Benchmark**: the mirror direction must average with it to exactly −0.094%.

In-sample result (175 markets, 870,223 hours): **+0.0465% ± 0.0395** on trade
count, **+0.0520% ± 0.0388** on volume.

## Why this is a candidate and not a finding

1. **The 4-hour horizon was not chosen in advance.** It won in an earlier run on
   flawed data, and I repeated it. That is selection — the mechanism behind
   every false positive of the last three months.
2. Volume and trade count measure nearly the same thing: two positives, one
   independent finding.
3. Twelve tests were run; about half a false positive is expected at 95%.

## The test, fixed before running

Two splits, both required to pass:

- **By market**: markets sorted alphabetically, odd-indexed form set A and
  even-indexed set B. The rule must hold **separately on both**. Markets are the
  only genuinely independent axis we have — horizons share entries, as learned
  this morning.
- **By period**: the first half of the hours versus the second half, separately.

**Success**: in all four cells the mean must be positive, and in at least three
the 95% interval must exclude zero.

**Failure**: any cell negative, or fewer than three cells above zero. Then the
candidate is dead and the in-sample result was the search.

No parameter may be adjusted after seeing this test. If it fails, it fails.

---

## Result: does not pass the bar I set

| | markets A | markets B | period 1 | period 2 |
|---|---|---|---|---|
| trade count | **+0.067%** ✓ | +0.027% | **+0.093%** ✓ | +0.014% |
| volume | **+0.076%** ✓ | +0.028% | **+0.076%** ✓ | +0.033% |

**Eight cells of eight positive.** The bar required at least three of four
demonstrated per measure; two hold. **Does not pass.**

### Honest on both sides

**For it:** eight positive signs with a consistent magnitude (+0.01% to +0.09%).
This is the furthest anything has come in the whole search, and the calibration
row was exact in every measurement that produced it.

**Against it, and it weighs more:** the **recent period is three times weaker**
than the first (+0.014% vs +0.093%). Either the effect is being competed away,
or it was never there and I am looking at noise with affection. And the eight
cells are not eight independent tests — they are the same data partitioned two
ways, with two measures that are nearly the same measure.

### Verdict

**Not promoted.** But not filed with the others either: this one did not
dissolve at the first check. New category — *failed the bar, survived the first
contact*.

Only more data resolves it, and Hyperliquid holds seven months. That means
another venue, with another pre-registration written before looking.

---

## Dead — the sign reverses on another venue

Tested with **identical parameters**, no tuning, on Binance futures:
**80 markets, 1,272,480 hours**, 22 months — a venue the search had never
touched and 1.5× the data.

| | Hyperliquid | **Binance** |
|---|---|---|
| fade after a volume spike | **+0.052%** | **−0.127% ± 0.034** |
| gross signal | +0.146% for fading | **−0.045% against** |
| both periods | positive | **both negative** |

Calibration exact here too (the two directions average to −0.10%, the declared
cost), so the measurement is sound and the result is real.

**When an effect changes sign across venues on 1.5× the data, it is not a weak
effect — it is noise that happened to point one way in one sample.**

This is precisely what the pre-registration existed for. Eight of eight
positive cells on Hyperliquid had convinced me enough to write a document about
it; without the test on fresh data I could have put money behind it.

Time to find out: **ninety minutes**, including building a 1.27-million-hour
dataset from scratch on a new venue.
