# The shortlist — step 3 done — 29 Oct

| | |
|---|---|
| borrowers scanned | 1,801 in **148 seconds**, zero failures (12.2/s) |
| **positions below health 1.15** | **140** |
| total debt watched | **$307 million** |
| **within 2% of falling** | **10 positions, $3.28M of debt** |

Those $3.28M sitting one small move from the threshold are worth roughly
**$130,000 of premium** at a 4% bonus.

And this comes from **1,801 of roughly 15,000 borrowers** — 6% of the list.
The full list implies about a thousand watched positions.

## A simplification that removes a whole component

I had planned to precompute, per position, the exact price at which it
tips. **That is not needed**, because failed attempts are free: when a hint
arrives, we attempt the positions nearest the threshold, and the ones that
did not fall revert at zero cost.

So the design loses a component instead of gaining one:

| | |
|---|---|
| ✅ contract that reverts unless profitable | compiles clean |
| ✅ reaction window | 6.47s median — thirty times what we need |
| ✅ shortlist of near-threshold positions | 140, refreshed in 148s |
| ~~exact tip prices~~ | **not needed — free attempts replace it** |
| → listener + bundle submission | next |
| → full test on a local chain copy | after |

Still zero euro, still nothing on-chain.
