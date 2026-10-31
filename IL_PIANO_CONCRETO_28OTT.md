# A concrete niche, named — 28 Oct

Counted by **actor** (not by contract), 43 days, 192 occasions, 49 actors of
which 17 are repeats.

| collateral | occasions | % to repeats | total | **unguarded** |
|---|---|---|---|---|
| **wstETH** | 14 | 57% | €80,845 | **€80,394** |
| **sUSDe** | 1 | 0% | €52,085 | **€52,085** |
| LINK | 9 | 89% | €21,711 | €13,421 |
| **rsETH** | 1 | 0% | €4,245 | €4,245 |
| USDT | 24 | 83% | €121,614 | €2,456 |
| USDC | 20 | 85% | €4,491 | €1,699 |
| WETH | **82** | 79% | €47,857 | **€856** |

**93% of all unguarded value sits in three collaterals.**

The contrast is the whole finding: WETH has **82 occasions and €856 left
unguarded** — fully occupied ground. wstETH has **14 occasions and €80,394
unguarded**.

## So the plan is specific

Configure the **staking and restaking derivatives** — wstETH, sUSDe, rsETH.
That is 87% of the free value (€136,724 of €156,710), and their unwind cost
was already measured: **0.01% to 0.23% at €200,000**.

| | |
|---|---|
| unguarded value, these three | ~€3,200/day |
| capital required | **none** — flash loan at 0.05% |
| cost of a lost race | **cents of gas** |
| what must be built | a contract that handles these three assets |

## The honest reservations

- **wstETH rests on 14 occasions** and is the solid leg.
- **sUSDe and rsETH rest on one each.** Two very large single events.
- Coverage is 72% of 60 days; the remaining windows could change the mix.
- Entering adds a competitor — the value is not simply waiting to be
  collected.

What makes this different from everything else in this search: the barrier
is **which assets someone bothered to configure**, and that is crossed with
work rather than with money or speed.
