# The 50-5 candidate survives, on 676 operations

Rule: enter when the curve's net reserve crosses 1.5 native. Sell at +50%, or cut at -5%.
All figures below already carry the real round-trip cost of 5.91%.

Sample: 3,345 curves followed, 676 closed positions (ten times yesterday's sample).

## Result

| | |
|---|---|
| average return per operation | **+6.80%** (interval +/-1.7) |
| first half / second half | +9.76% / +3.84% |

The interval no longer contains zero. On 60 operations it did.

## How the operations end

| outcome | how many | share | average | contribution |
|---|---|---|---|---|
| target +50% | 177 | 26.2% | +41.63% | +10.90 pts |
| stop -5% | 344 | 50.9% | -10.30% | -5.24 pts |
| neither | 155 | 22.9% | +4.97% | +1.14 pts |

Half the operations lose. The rule works because one in four pays +41.6% and the losses
are capped at -10.3% (the -5% stop plus the 6% cost).

## The four attacks

1. **Remove the luckiest.** Without the 50 best operations: +4.02%. Not a few lucky hits.
2. **Split the timeline in four.** +15.13%, +4.39%, +2.28%, +5.39%. Positive in all four.
3. **Resample 1,000 random halves.** Worst 5%: +5.40%. Zero of 1,000 halves negative.
4. **Kill the unresolved group** (22.9% closed at a paper price): if they exit at break-even
   instead, **+4.38%**. Only if they were worth nothing at all does the rule die (-17.27%),
   and they cannot be: a bonding curve always quotes a bid.

## What is still not proven

These are simulations on recorded paths, not executed operations. The forward test with the
frozen rule is the judge, and it needs more days. The second half earns less than half the
first: either the market is cooling or the first half was lucky.

Not calling this a solution yet.
