# Where the uncertainty actually lives — 23 Oct, late

| component | mean | stdev | precision now | n needed for ±0.5% |
|---|---|---|---|---|
| **fees collected** | **+2.09%** | 3.2 | **± 0.09** | **161** |
| price drift | −1.35% | 29.4 | ± 0.81 | 13,282 |
| net | +0.74% | 30.3 | ± 0.83 | 14,125 |

**The fee income is not in doubt.** +2.09% per two-minute position, known to
nine hundredths. All the uncertainty sits in one number: how far a graduated
coin drifts in the two minutes after minute one.

## This invalidates the forward test I registered

With a per-position stdev of 30 points, 200 positions give ±4.2% — against a
target value of 0.6%. **Test 3 cannot decide anything**, even if the strategy
works. Resolving it that way would take ~14,000 positions, about 300 days at 46
graduations a day.

The right question is narrower and much cheaper: **measure the drift**, which
needs only two prices per coin, not a valid position.

## And the trap I nearly walked into

Measured on the widest sample (5,084 coins), the drift is **−0.63% ± 0.78**,
which would make the net **+1.46%, interval [+0.59%, +2.32%] — positive even at
the worst end**.

But the same drift on the position sample (5,110 coins) is **−1.35% ± 0.81**.
Two nearly identical samples, 0.7 points apart. The difference is inside the
noise, so neither is wrong — but **picking the friendlier of two compatible
estimates and announcing it is exactly the mechanism behind every false positive
of the last three months.**

**Honest reading: net between +0.7% and +1.5%. Probably positive, not proven.**

Next: find out *why* two near-identical samples differ — noise, or a filter that
quietly selects better coins. That matters more than accumulating positions.

---

## Resolved: 59 coins out of 5,143 explain the whole gap

The two estimates differed because of the **stuck positions** — coins with no
sell print inside the window. Dropping them gives −0.63%; counting them at
−100%, as our rule requires, gives **−1.77%**. A 1.14-point swing produced by
**1.15% of the sample**.

**Correct net: +2.09% − 1.77% = +0.32%, interval [−0.59%, +1.23%].** Not
demonstrated, and the central estimate is a quarter of what it looked like an
hour ago.

### Worse, crossed with the capacity curve

| capital | fees | drift | **net** |
|---|---|---|---|
| 200 | +2.06% | −1.77% | **+0.29%** |
| 1,000 | +1.96% | −1.77% | **+0.19%** |
| 5,000 | +1.59% | −1.77% | **−0.18%** |

**At the size that would make it a machine, the central estimate is negative.**
At EUR 1,000 the central case is about EUR 9 a day, with an interval containing
zero.

### Where the remaining hope is, precisely

Not in earning more fees — in **reducing the drift**. And the drift is not a
gently falling average: it is **1% of coins dying inside two minutes and taking
the whole position**. That is a tail, and a tail can sometimes be refused in
advance — by declining coins that have no buyer. That is the next measurement.
