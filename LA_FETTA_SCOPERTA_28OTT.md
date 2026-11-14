# Where the professionals are not looking — 28 Oct

We cannot win a speed race against twenty bots on dedicated nodes. But
"cannot win where everyone races" is not "cannot win". So: classify the
winner of every occasion over €100 as a **repeat player** (3+ occasions) or
an **occasional**, and look for a slice where the repeats are absent.

## The slice is the collateral asset

| collateral | occasions | won by repeats | value |
|---|---|---|---|
| WETH | 24 | **79%** | €47,329 |
| **USDT** | 5 | **20%** | **€121,490** |
| wstETH | 4 | 50% | €80,642 |
| **sUSDe** | 1 | **0%** | **€52,085** |
| LINK | 4 | 75% | €21,607 |
| AAVE | 4 | 50% | €11,018 |
| WBTC | 4 | 75% | €5,481 |
| USDC | 5 | 80% | €4,390 |
| **rsETH** | 1 | **0%** | €4,245 |

The professionals hold **WETH** — the obvious asset, 24 occasions, 79%
theirs, and the **lowest value per occasion**. Where the real money is —
USDT and the exotics — the **occasionals** win.

## And there is a reason that is not speed

The two unidentified tokens are **sUSDe** (Ethena's staked dollar, oracle
price $1.25) and **rsETH** (Kelp's restaked ETH, $2,516). Together with
wstETH, every under-covered slice is a **yield-bearing or restaked**
collateral.

**sUSDe cannot be sold instantly** — redemption has a cooldown, so a
liquidator taking it must either hold it or sell into a secondary market at
a discount. rsETH has its own separate liquidity. A bot that only knows how
to swap WETH on Uniswap **cannot handle these**.

If that is the reason, the barrier on that slice is **not latency but
knowing how to unwind awkward collateral** — a barrier crossed with work,
not with faster nodes. That is the first barrier in this whole search that
is on our side of the line.

## Stated plainly: the numbers are small

5 occasions of USDT, 1 of sUSDe, 1 of rsETH. This is a **lead**, not a
result. It needs the remaining coverage, and then the decisive measurement:
**can that collateral actually be sold, and at what discount?** If sUSDe
only moves at −8%, the premium is gone and the slice is uncovered for good
reason.

---

## The awkward collateral sells fine — my own explanation was wrong

I proposed that professionals skip sUSDe and rsETH because they cannot unwind
them. Quotes from CoW Protocol (free, keyless, the same prices a real seller
would get), selling €200,000 worth:

| collateral | sold into | discount |
|---|---|---|
| sUSDe | USDC | **−0.11%** (you receive *more* than oracle value) |
| rsETH | WETH | **0.23%** |
| wstETH | WETH | **0.01%** |
| WETH | USDC | −0.31% |

Against a 4–5% premium, a 0.23% unwind cost is nothing. **The hypothesis is
false** — these assets have deep liquidity even at €200k, and the slight
negative discounts suggest the oracle lags the market a little.

So the remaining explanation is the simplest and the most favourable one:
**the professionals have not configured those assets.** A coverage gap, not
an economic barrier.

## Where the candidate stands

Every test built to kill it has been run, and it is still standing:

| test | result |
|---|---|
| capital gate | **none** — flash loans |
| network congestion on the days that pay | **absent** — 0.4 gwei |
| bidding war for the premium | **none** — €98,150 taken for €0.20 of gas |
| related-party liquidations | **excluded** — 16 of 16 are professional contracts |
| awkward collateral unsellable | **false** — 0.23% at €200k |

What remains is the honest weakness: the uncovered slice is **7 occasions**
in the sample. The lead is real; its size is not yet measured.
