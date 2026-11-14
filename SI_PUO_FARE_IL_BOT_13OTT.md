# Can a bot buy and sell inside the curve? Seven attacks, six failed

The target of demolition changed today: no longer "the edge is not real" but "the tool
cannot be built". Everything below is measured against the live node and real transactions
of other people. Nothing is estimated. Cost of this work: zero (public RPC, no keys).

## The seven attacks

| # | attack | measurement | verdict |
|---|---|---|---|
| 1 | we are too slow | read trades 417ms, 5 blocks pass while reading, send 172ms, inclusion 100-200ms = **~1 second** | **failed** - edge holds to 10s, dies at 30s |
| 2 | gas explodes when everyone runs | 0.0201 gwei, identical in empty and busy blocks; a sell costs **0.0072 EUR** | **failed** |
| 3 | snipers outbid us for priority | in 300 blocks, whoever pays 4.7x more lands in position 4 of 12 - blocks are not ordered by price | **failed** |
| 4 | sells revert on price protection | **0 failures of 66** direct curve calls (chain-wide revert rate is 24.4%, concentrated in other contracts) | **failed** |
| 5 | the node cuts us off | 60 parallel requests: zero errors, median latency *drops* to 177ms | **failed** |
| 6 | the contract locks us in | 3,153 buy->sell pairs: **minimum wait 0 blocks**, 3 sold in the same block, 71 within one second | **failed** |
| 7 | our own buy moves the price | a 30-80 EUR buy moves it **+1.19%** (8,510 real buys compared in pairs) | **failed** |

## The one hit that landed

**One wallet serialises the sells.** 51% of exits fall within one second of the previous
one - and the figures at 1, 2 and 5 seconds are nearly identical (283, 283, 285), so exits
are not spread out: they **cluster in the same instant**, triggered by the same market move,
exactly when a lost second costs most.

Requirement: **one wallet per slot, ten wallets.** Cost of the cure: zero.

## The latency budget, in full

| step | measured |
|---|---|
| read the trades of the last second | 417 ms |
| blocks passing while we read | 5 blocks = 500 ms |
| send the sell | 172 ms |
| land in a block | 100-200 ms (block time 100 ms) |
| **total** | **~1 second, 1.5s worst case** |

Return against delay (recorded paths, real 5.91% cost included):

| delay | 50-5 | stop -2% / 2x | stop -2% / 3x |
|---|---|---|---|
| instant | +7.82% | +8.49% | +5.49% |
| **1 second** | **+6.52%** | **+6.21%** | +2.11% |
| 10 seconds | +6.26% | +5.20% | +1.59% |
| 30 seconds | +1.01% | +0.47% | -3.25% |

Measured from a laptop in Italy. A machine near the node would be faster; the node is public
and shared, so it may slow down exactly when it matters.

## Verdict

**The bot can be built.** No structural obstacle was found: not speed, not gas, not priority,
not reverts, not rate limits, not contract locks, not market impact. The only requirement
discovered is ten wallets instead of one.

This is a statement about feasibility, not about profit. Whether the strategy earns is a
separate question, still open, answered only by the frozen forward test.
