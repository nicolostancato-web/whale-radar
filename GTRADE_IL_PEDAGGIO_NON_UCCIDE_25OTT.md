# gTrade: the first venue where the toll is not the killer — 25 Oct

The widened question produced its first measured candidate: **gTrade** on
Arbitrum, a permissionless venue for FX and commodity exposure.

## Identification, verified not remembered

- `0x18c11fd2…` declares itself **"Gains Network" (GNS)**
- `0xff162c69…` emits **`GovFeeCharged`** — a name specific to gTrade — 275
  times in 2.8 hours
- the contract itself declares its collaterals: **DAI, WETH, USDC, GNS**

## The size

**EUR 2,346 a day** from the governance fee line alone — and that is one line of
several. For scale: UniswapX's entire pie on Base was EUR 40/day, Morpho's
liquidation premium EUR 94/day. **Two orders of magnitude bigger.**

## The toll, on notional

First attempt divided the fee by the **margin** and gave 7.23% with quartiles
1.27%–44.5% — the shape of a fixed rate seen through varying leverage. Leverage
is readable from the contract (`getTrade`, word 3, 1e3 precision; word 6 reads 3
and the contract separately declares collateral 3 = USDC, which is how I know
the fields are the right ones).

| | |
|---|---|
| **governance fee on notional** | **0.0474% median** (quartiles 0.0064% / 0.3995%) |
| for comparison, memecoin total toll | **6%** |

**For the first time in three months, the cost of moving is not what kills the
trade.** Two orders of magnitude.

## And the thing I was not looking for

**Median leverage is 150×**, with observed values up to **500×**.

At 150× an adverse move of **0.67%** liquidates the position. EUR/USD moves
about 0.5% on an ordinary day. So in that venue people are not killed by fees —
**they are liquidated before they turn out to be right.**

This moves the question to something answerable: *can one sit in that market at
low leverage, where the toll stays negligible and liquidation does not arrive?*
