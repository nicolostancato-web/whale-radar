# The sale problem, solved generally — 31 Oct

Chasing individual venues was the wrong approach: every collateral has its
own maze. sUSDe does not trade on Uniswap; its Curve pool exits into DOLA,
whose only route onward has **$14,394** of liquidity — a dead end.

The right answer is an **aggregator**: it finds the route itself, combines
venues in one call, and our contract already executes arbitrary calls.

## Paraswap, measured with executable calldata

| collateral | value | slippage | API response |
|---|---|---|---|
| sUSDe → USDT | $250,000 → $250,657 | **−0.263%** | 1.08s |
| wstETH → USDC | $279,400 → $276,422 | +1.066% | 1.02s |
| WBTC → USDT | $154,238 → $154,114 | +0.080% | 0.90s |

**One second to answer.** The window measured on the real event was seven
seconds, so this fits with five to spare.

## A correction I owe

Days ago I reported that the awkward collateral "sells at 0.01–0.23% on
€200,000", based on a CoW quote. **For rsETH that was false.** Two
execution-level tests now disagree with it:

- Uniswap on a fork: **10 rsETH → 8 USDC**
- Paraswap: `ESTIMATED_LOSS_GREATER_THAN_MAX_IMPACT — 97.58%`

The CoW figure was an indicative quote, not something a solver would fill.
**An indicative quote is not an execution.** rsETH is excluded from the
target list: it was worth €4,245 across the two measured months, the least
of the five.

## Contract change

The contract now accepts a **chain of sale steps** rather than one, because
some collateral cannot be unwound in a single hop. The full end-to-end test
still passes with the same result ($25,174 on the fork).

## Architecture, settled

```
see the fall          (polling, every 3s)
ask for the route     (aggregator, ~1s)
send the liquidation  (immediate)
```

Works for any collateral, including ones we have not seen yet.
