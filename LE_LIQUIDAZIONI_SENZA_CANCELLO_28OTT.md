# Liquidations: the first trade with no gate — 28 Oct, partial

Fifteen families ended the same way: either nothing is paid, or entry costs
capital. Liquidations are the one candidate where **neither applies**, and
the reason is specific: with a **flash loan** you liquidate without putting
up a euro — borrow, repay someone else's debt, take the collateral premium,
return the loan, all inside one transaction. If it is not profitable it does
not execute. Only gas is at risk.

## Measured so far

**Base** (Aave v3, 1 day, 0% of windows failed): **2 liquidations**, both
taken by the same address. Tiny and monopolised.

But Base was chosen because I already had the connection there, not because
it is where liquidations happen — the "sample of myself" error that has bitten
three times in two days. So, **Ethereum**:

| Aave v3 on Ethereum, 2 days, 32% of windows failed | |
|---|---|
| liquidations | 6 observed → **~4.4/day** adjusting for coverage |
| **distinct liquidators** | **5 out of 6** |
| share of the biggest | 33% |
| share of the top three | 67% |

**Not monopolised.** Five different actors in six events is the profile of a
distributed trade, the opposite of Base and the opposite of what a
speed-monopoly looks like.

The failure count is reported because silent zeros once made Kleros look dead.
A first pass at 80% failure would have given "0.9/day" — wrong by five times.

## What is still missing

**What one pays.** The measurement is running: decoding the seized collateral
for the assets whose currency and decimals I know (WETH, USDC, USDT, DAI,
WBTC, cbBTC), counting the others separately rather than as zero.

Until that number exists, this is a trade with an open door and an unknown
wage — which is exactly the thing worth finishing.
