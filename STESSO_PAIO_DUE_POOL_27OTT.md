# The same pair in two pools — the eighth road, closed — 27 Oct

After all seven architectures closed, the enumeration itself was questioned.
One category had been missing: **being paid because a protocol's rules make an
outcome certain** — not prediction, but reading code. The only deterministic
thing this project ever found (the 12.25x graduation on Pons) belongs there.

The cheapest instance: the **same token pair living in several pools on one
chain**. The round trip is **atomic** — one transaction, and if it is not
profitable it simply does not happen. Gas is at risk, never a position. No
four legs, no waiting, no price risk. It is the one shape where the toll that
killed everything else does not apply.

## The measurement

30 minutes of Base: 35,953 swaps, 1,292 pools, **93 pairs present in more than
one pool**.

| pair | comparable blocks | median gap | blocks above the two fees |
|---|---|---|---|
| USDC / 0x5be7… (4 pools) | 869 | 0.000% | **0%** |
| 0x4200… / 0xcbb7… (11 pools) | 383 | 0.000% | **0%** |
| 0x4200… / 0xb200… (3 pools) | 174 | 0.062% | **0%** |
| USDC / 0x1103… (2 pools) | 186 | 0.000% | **0%** |
| USDC / 0xb200… (2 pools) | 6 | 1.314% | 100% |

Wherever there is activity, the pools are held together **below the fee**.
The arbitrage is fully captured. Only the last row shows a persistent gap —
and it has 6 comparable blocks out of 900, meaning a pool that barely trades.

## A correction to my own arithmetic

My first instinct was to value that gap as 1.31% of the volume flowing
through — $33 per half hour. **That number does not exist.** An atomic
arbitrage collects the gap **once**, on the size that can be pushed before the
two prices meet; it does not collect a share of other people's swaps.

What matters is depth, and the trade sizes say it plainly: **$24 and $28**.
The pools where the gap survives are nearly dead, and the capturable amount is
a few dollars.

## Verdict

Closed, and closed for the reason that has now closed nine things in a row:
**not the signal — the capacity.** Where money flows, competition compresses
the gross below the toll; where the gross survives, no money flows.
