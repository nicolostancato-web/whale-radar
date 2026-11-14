# The edge is in the entry, not in the rule

Attack run: "best of many". If the +6.80% of the 50-5 rule came from picking the best of a
handful of rules on the same data, widening the grid should expose it.

Grid: 7 stops x 7 targets = 49 rules, on 680 closed positions. Real cost 5.91% included.

## Result: the whole family is positive

- 39 of 49 rules positive. Median of the entire grid: **+5.76%**.
- Best: stop -2%, target 3x -> **+22.93%**. Worst: stop -50%, target +10% -> -4.28%.
- 50-5 ranks **20th of 49**. It is not special.

The surface is smooth and monotone - the higher the target and the tighter the stop, the
better the return. Overfitting produces an isolated jagged peak. This is not that shape.

| stop \ target | +10% | +20% | +30% | +50% | 2x | 3x | never |
|---|---|---|---|---|---|---|---|
| -2% | -1.3 | +1.4 | +3.2 | +6.8 | +14.1 | **+22.9** | +18.0 |
| -5% | -1.7 | +1.2 | +2.9 | +6.8 | +14.1 | +22.4 | +17.5 |
| -10% | -2.0 | +0.8 | +2.5 | +6.5 | +13.0 | +21.0 | +15.9 |
| -20% | -2.4 | +0.3 | +2.1 | +5.7 | +10.9 | +18.8 | +13.3 |
| -50% | -4.3 | -2.5 | -0.9 | +2.6 | +5.8 | +12.5 | +6.1 |

## Out of sample

Rule chosen looking only at the first half, measured on the unseen second half:
**+7.49% (+/-4.4)**. Down sharply from +37.25% in-sample, as always, but still positive
with an interval clear of zero.

## The best rule is not a two-lucky-hits story

Stop -2%, target 3x: **87 of 680 positions reach 3x** (12.8%). Removing the 20 best
operations still leaves **+18.07%**.

## Frequency

680 positions over 1.78 days = **383 opportunities per day**. Opportunities are not the
bottleneck.

## Still not proven

These are simulations on recorded paths. Nothing has been bought or sold. A 3x target takes
much longer to resolve, so the share of unresolved positions grows - that is the next attack.
