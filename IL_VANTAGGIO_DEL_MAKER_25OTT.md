# The maker advantage, measured: 0.011% per cycle, not 0.06% — 25 Oct

The surviving candidate's whole margin rested on paying 0.04% instead of 0.10%
per cycle — that is, on posting an order rather than crossing the spread. I had
**assumed** that saving. Here it is measured, on 30 markets and 477,300 hours.

## The measurement, with horizons aligned

First attempt compared a filled maker (window starting at k+1) with a market
buy (window starting at k) — two different horizons, so the difference mixed
adverse selection with a one-hour offset. Redone with both exiting at the same
instant:

| | return | n |
|---|---|---|
| posted and filled | −0.0260% ± 0.0251 | 67,627 |
| crossed the spread | −0.0017% ± 0.0241 | 68,130 |
| **not filled** | +0.3586% ± 0.2822 | 503 |

- **fill rate: 99.3%** (upper bound: it assumes being at the front of the queue)
- **entry price is worse by 0.0243%** — you are filled precisely when the market
  comes to you, which is when it is going against you
- commission saved: +0.0300% per leg

> **Net maker advantage: +0.0057% per leg. Two legs: +0.011%, not +0.06%.
> Five times smaller than assumed.**

## It kills the candidate

Recomputing the cross-market reversal with the measured constant instead of the
invented one: from **+0.0756%** per cycle to about **+0.027%**, against an
interval of ±0.08%. Inside the noise, definitively.

This is the same error I forbade myself two days ago with the 0.30% fee: **a
plausible constant in place of a measurement**, wrong by a factor of five both
times. The difference is that this time I looked for it before telling Nicolò
it worked, not after.

## What survives, and is reusable

**The maker advantage in this environment is about one hundredth of a percent
per round trip, not six.** Measured over 68,000 cases. It replaces the
assumption in every future calculation — and it means any strategy whose margin
depends on "we will post rather than cross" has almost no margin at all.
