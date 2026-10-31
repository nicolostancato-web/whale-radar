# Flashbots accepted our bundle — 31 Oct

```
bundleHash:   0xf31f96c24ded0cce2751c289c4756d6f2e25d7764e92a5e8a995fb92c38652dc
block:        26312656
sender:       0x4355962379C779009F833d81bd8D2912773749A0
result:       EXECUTED in simulation
```

That hash is the receipt Flashbots assigned **to our reservation**. The
bundle was well-formed, accepted, and would have entered block 26312656.

This is the technical definition of what was asked: **we can be in the same
block as the professionals.**

## The full chain, all verified today

| | |
|---|---|
| see the price update before the block | ✅ 17 in 4 minutes on MEV-Share |
| time available to react | ✅ **6.47s median**, we need under 1 |
| compose the liquidation call | ✅ **1.09 seconds** |
| sign the transaction | ✅ |
| **Flashbots accepts and simulates** | ✅ **bundleHash issued** |

## What this is not, stated plainly

The transaction sent was **an innocuous call** — the contract reading its own
cassa address. It proved the **chain**, not a liquidation: no position is
currently below the threshold.

And "simulated" is not yet "included". Flashbots confirms the bundle is valid
and executable; actual inclusion is the builder's decision when the moment
comes.

**The door is open and we walked through it. The shot has not been fired.**

## Why this changes the strategy

Yesterday's measurement said every large occasion — all ten of them,
professionals and occasionals alike — was taken **in the same block** it
became liquidatable. With a polling design we could never win those: we are
always one block behind.

With a bundle, we are not behind. We reserve the seat before the bus arrives.

## What is left

Attach the bundle to a **real hint** when a price update passes, instead of
the test payload. That is the last wire.
