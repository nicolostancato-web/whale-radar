# Three chains, one instrument, six dead positives (20-22 Oct)

The founder refused to let Robinhood be abandoned on a sloppy audit, and was right: the audit
found that we had measured 13% of that chain. Widening it, and then porting the same calibrated
instrument to Base and Solana, produced the clearest two nights of the project — and not one
surviving edge.

## The instrument, which is the actual asset

Every table now carries a **calibration row**: buy and sell back immediately. It must be
negative and proportional to the pool's fee. If it is not, the row is not read. Plus three
rules paid for in blood: the verified sign of a trade, entry at a buy print and exit at a sell
print, and the same operations in every horizon column.

It was validated independently on all three chains:

| chain | reader | calibration |
|---|---|---|
| Robinhood | Uniswap v4 logs | passes on fee-bearing pools, **fails on Pons** (hook skims after the swap, invisible in the data) |
| Base | same code, unchanged | passes, proportional: fee 0.30% → -0.60%, fee 1.00% → -1.97% |
| Solana | **written from scratch**, reads the signer's balance change | passes: -3.85%, -4.05%, -3.77% on three tokens |

The Solana case matters most: a brand-new reader, validated without anyone having to trust the
person who wrote it.

## The six positives that died

| what it looked like | what it was |
|---|---|
| +172% arbitrage at graduation | a stale curve price and an 80-coin sample of our own files |
| +64.79% mean gap | the last curve buy picked without breaking ties inside the block (the curve rises 12.25x by construction) |
| +20 points of wallet skill | specific to one of three periods |
| +0.46%/+0.59% outside Pons, replicated twice | **the sign of a trade was inverted**: the tell was the return equalling exactly twice the pool fee |
| +0.94% on freshly born Base pools | **82% of positions had nobody to sell to** |
| +0.94% where the market is quiet, on 2.8M operations | **Pons' invisible toll**; on Base, where the toll is visible, the gradient is exactly +0.00 |

Each was caught by the instrument, not by intuition. Each tell was a regularity too clean to be
a market: a return equal to twice a fee, a calibration that turned positive, a gradient that
vanished when the chain changed.

## What the three chains say together

| position | Robinhood | Base | Solana |
|---|---|---|---|
| following a buy | -6.87% at our latency | flat at minus the toll, every horizon | calibration passes, first readings mixed |
| copying wallets | real skill, absolute -4% to -13% | median worse than random; the "best four" are one operator | identity comes free with the reader |
| being the launcher | EUR 0.55 against EUR 1.71 | — | — |
| providing liquidity | fee 0, the protocol takes it | real fees exist outside the launchpad | — |
| arbitrage | +0.58% against a 6% toll | 3.06% against a 12% toll | — |

Two different walls, measured: on Robinhood there is always a counterparty but the toll eats
everything; on Base's newborn pools the toll is normal but **82% of positions cannot be sold at
all**. Where both problems are absent — liquid pools with visible fees — the return is exactly
minus the toll, at one minute, five minutes and thirty.

## Cost of the two nights

Zero euros. Cash unchanged at EUR 52.16 for eight days. 1,552 Helius credits (0.15% of the free
monthly allowance), 9.5 cents of external review, and seven public RPC endpoints tested one by
one rather than trusted.
