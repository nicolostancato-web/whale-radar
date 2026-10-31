# Pre-registration — gold breakout, copper breakdown — 25 Oct, before the test

Written **before** running the test. The candidates below were found by scanning
126 rules on hourly data; that scan **burned the holdout**, so they are
candidates, not findings.

## The two candidates, and why these two

Of 13 rules that beat random entries on the same market and horizon (against ~3
expected by chance at 126 tests), only two show **internal coherence** — several
variants of the same idea agreeing, rather than opposite rules both winning,
which on silver revealed market drift rather than skill.

**A — Gold, breakout above the recent high.**
Variants all positive against random: lookback 24h at 6h (+0.112% ± 0.078),
lookback 72h at 6h (+0.142% ± 0.091), lookback 24h at 24h (+0.255% ± 0.180),
lookback 72h at 24h (+0.418% ± 0.209).

**B — Copper, entry below the recent low.**
Lookback 24h, at 6h (+0.144% ± 0.128), 24h (+0.420% ± 0.234), 72h (+0.380% ± 0.367).

## The test, fixed now

- **Data never used**: the 10-year **daily** series for gold and copper, a
  different series at a different frequency from the hourly data that produced
  the candidates.
- **Rule A**: enter at the close of a day whose close exceeds the highest high
  of the previous 24 periods; exit after 6 and after 24 periods.
- **Rule B**: enter at the close of a day whose close is below the lowest low of
  the previous 24 periods; exit after 6, 24 and 72 periods.
- **Benchmark**: not zero — the mean of random entries on the same market and
  the same period, as the silver lesson requires.
- **Cost**: 0.05% per round trip, the measured gTrade toll.
- **Success**: the difference from random must be positive with its 95%
  interval excluding zero.
- **No new rules may be added after seeing this test.** If both fail, the
  candidates are dead and the hourly result was the scan.

## Known weakness, stated in advance

Daily candles are not hourly candles: a rule that works on one frequency need
not work on the other, and a failure here is not proof the hourly effect was
noise. It is, however, the only unseen data I have, and a candidate that cannot
survive a change of frequency is not one I would risk money on.
