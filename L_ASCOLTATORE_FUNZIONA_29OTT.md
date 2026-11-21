# The listener works — step 4 done — 29 Oct

Dry run, nothing sent, no key, no money.

| | |
|---|---|
| hints received | **5,503 in 8 minutes** (~690/min, steady) |
| price updates detected | **25** |
| **time available at each one** | **6.1 – 6.7 seconds** |
| reconnections | 1 |

The reaction window is no longer an estimate computed afterwards — the
program **prints it as it happens**. Every time a price update passes, we
have over six seconds. We need two tenths.

## The bug that was worth finding

The first version collected **111 hints in ten minutes instead of ~5,500**,
and **did not complain**. The stream had stalled and `readline` sat waiting
forever. I would have built everything on top of a deaf ear and concluded
"there are no opportunities".

Fixed with a liveness timeout and reconnection: if twenty seconds pass with
no event, it reconnects. One reconnection was needed in eight minutes, so
the stall is real and recurring — a listener without this would be useless
within the hour.

## Build status

| | |
|---|---|
| ✅ contract, reverts unless profitable | compiles clean |
| ✅ reaction window | 6.1–6.7s, confirmed live |
| ✅ shortlist of near-threshold positions | 140, refreshed in 148s |
| ✅ listener, resilient to stalls | 690 hints/min |
| → bundle construction | next |
| → full test on local chain copy | after |

Zero euro. Nothing on-chain.
