# It works — the full sequence, end to end — 29 Oct

On a local copy of the chain, forked at block 26198342:

```
starting health          1.0043   (not liquidatable)
price drop of 2%
health after             0.9872   (fallen)
flash loan               400,000 USDC
liquidation              executed
collateral sold          executed
loan repaid              + 0.05% fee
PROFIT                   $25,174
```

**Every link exists and runs**: borrow, liquidate, sell, repay, profit — in
a single transaction, starting from zero capital.

## Honesty about the number

**$25,174 is inflated by my own simulation.** I lowered only Aave's oracle,
not the real market, so the contract buys collateral at a discounted price
and sells it at the full one — a gap that does not exist in reality.

The real profit on a 400,000 liquidation would be the protocol's bonus
alone: roughly **$16,000–20,000**, not 25. The test proves the *mechanism*,
not the size.

## Two of my own errors, both invisible from reading the code

1. **"Sell zero."** The swap call needs the amount of collateral, which is
   only known *inside* the transaction. I was passing zero. Fixed: the
   contract now writes the real amount into the call itself, at an offset
   given in the plan.
2. **Loose fields instead of a struct.** The router wants a structure, which
   needs a pointer in front. Passing the fields separately produced
   unreadable calldata — `InvalidFEOpcode` after 506 gas. Fixed by declaring
   the interface so the compiler encodes it.

Neither would have been found by reading. Both were found in minutes by
running it where money does not exist.

## Six pieces of six

| | |
|---|---|
| contract, reverts unless profitable | ✅ |
| reaction window 6.47s | ✅ |
| shortlist of near-threshold positions | ✅ |
| listener, 690 hints/min | ✅ |
| Flashbots authentication | ✅ |
| **full sequence on a local chain copy** | ✅ |

**Zero euro spent. Nothing on-chain.**

What is left before a real attempt: a wallet with €15–20 of gas, and
Nicolò's word.
