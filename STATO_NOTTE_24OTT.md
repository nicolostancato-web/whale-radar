# Night of 23→24 Oct: three roads closed, one parked on a clock

| # | road | verdict |
|---|---|---|
| 9 | refuse the merchant's tail in advance | **closed** — the best filter on the first half is the worst on the second; the gain was the search |
| 10 | overnight liquidity on tokenized equities | **closed** — the equities are real (NVDA, SPCX = SpaceX) but 1 pool of 917 is an equity; the market lives inside Robinhood's app |
| 11 | UniswapX fills after the exclusive window | **closed on capacity** — live and open (428 fills/10h, 20 solvers, top one 35%), but ~EUR 40/day for the whole chain, ~EUR 2/day for us |
| 12 | leveraged tokens (AAPLx3L) | **parked until US hours** |

## Why road 12 is parked rather than tested

`AAPLx3L/USDG` moves **EUR 27M a day** with a **0.00% fee** — real size, but no
fee means no merchant income there; the candidate trade is arbitrage against the
token's theoretical value (3× Apple's move), which costs only gas at zero fee.

At 03:00 Italy the pool shows **zero swaps in 1.6 hours**: New York is shut,
Apple is still, and a 3× Apple token does not move. Measuring now would describe
a stopped market — the same population error as before, with a clock instead of
a filter. **It measures properly between 15:30 and 22:00 Italian time.**

That constraint is good news: it is the only one of the twelve roads whose
limitation is an opening time rather than an uncertainty.

## Still accumulating by themselves

- forward test 3 of the two-minute merchant (graduated pools only), 5/200
- UniswapX solver profit, a few fills per pass inside the RPC's 8-minute state
  window
