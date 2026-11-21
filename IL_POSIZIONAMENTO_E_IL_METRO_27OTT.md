# Positioning data, and the first calibrated yardstick — 27 Oct

After the correction (on perpetuals the wall is the signal, not capacity), the
search moved to the most different data left: **positioning** — who is in and
on which side, rather than what the price did. Three free hourly series from
Binance, 30 days deep: open interest, the long/short account ratio of large
accounts, and the share of aggressive buying volume.

297 markets, 148,194 hours, 108 paired class tests — one-sided (long), entry
one hour **after** the signal, non-overlapping, each rule against the same
number of long entries at shuffled times.

| variable | median t, real | shuffled | difference |
|---|---|---|---|
| open interest | −4.847 | −5.262 | +0.416 |
| long/short account ratio | −5.529 | −6.870 | **+1.342** |
| aggressive buying share | −10.236 | −8.263 | **−1.973** |

(Everything is deeply negative because the market fell hard across these 30
days; the difference against shuffled entries is the statistic that removes
that.)

## The yardstick, which is the real result

This morning a class test of exactly this shape produced a difference of
**+2.238** — and that candidate then died on 173 held-out markets, with every
interval containing zero.

So today, **by measurement rather than by caution, 2.2 units of difference is
inside the noise of this design.** Everything above is below that floor.

Until now "that's small" was a judgement. Now it is a comparison against a
documented false positive, with a number attached. That is the first
calibrated threshold this project has had, and it is worth more than the
result it just rejected: every future class test can be read against it
immediately, instead of costing a held-out sample to find out.

## Stated limitation

The public positioning archive is **30 days**. A real effect that only shows
over longer horizons could not appear here. This closes the family as
*measured over a month*, not forever.
