# An anomaly that survived three checks — 24 Oct, morning

Searching for a place where **our size is not the binding constraint**, one
candidate appeared: a pool between two assets that cannot diverge.

## The pool

`0x9ab7730b09ebd9ff2df70f06339bd289a1680a46` — **USDC/USDT on Base, 0.30% fee**

| measured over 6 hours | |
|---|---|
| swaps | 3,773 |
| volume | USD 811,349 — **17× its own capital** |
| capital in the pool | USD 47,795 |
| fees paid by traders | ~USD 2,434 |
| implied yield for LPs | **~15% a day** |

Right beside it sits a **0.00% fee** USDC/USDT pool holding **USD 605,000**,
which over the same six hours did **less** volume.

## What EUR 52 would actually earn

Fees go only to **in-range** liquidity, so the honest share comes from the
`liquidity` field inside each Swap, not from the pool's balance:

| band around price | our share of active liquidity | per day | annualised |
|---|---|---|---|
| **±0.05%** | 0.02% | **EUR 1.69** | **~1,089%** |
| ±0.20% | 0.01% | EUR 0.42 | 272% |
| ±1.00% | 0.00% | EUR 0.08 | 55% |

Concentrating is safe **here specifically**: the two assets cannot drift apart,
so the adverse selection that destroyed the memecoin merchant does not apply.
Observed price range over three hours: 1.001660 to 1.001748.

## Three checks it survived

1. **It is not a 30-minute burst.** Sustained across six hours, 3,773 swaps.
2. **It is not my arithmetic.** Both sides of the pool counted; the first
   reading (11,424%) was one side doubled and was withdrawn.
3. **It is not a carousel.** Over twelve hours: **zero Mint, zero Burn, zero
   Collect**. Nobody is cycling the position, and the owner is not even
   harvesting. Twenty-eight distinct addresses trade, the busiest at 39%.

## What I cannot explain, and therefore what this is not yet

**Why do twenty-eight addresses pay 0.30% when a free pool sits next door?**

Until that is answered this is not an opportunity, it is an anomaly. But it is
the first anomaly in three months that survived three consecutive checks
instead of dissolving at the first.

### Required before a single euro moves

1. Why those traders pay — routing, an incentive, or something invisible here.
2. That a **new** position actually accrues fees (mint, wait, read `Collect`).
3. Entry and exit cost, and the depeg risk: if one leg loses parity we are left
   holding it.

---

## Explained, and it was my own error — same morning

The pool does not implement `fee()`. My code said: *if the call fails, assume
0.30%.* That fallback carried three hours of analysis and four successive
measurements — each correct in itself, all built on a number I invented.

**Measured instead of assumed**, from 682 consecutive swaps (ΔsqrtP and the
`liquidity` field give the fee-free input; the excess is the fee):

> **fee = 0.0004%**, quartiles identical. Not 0.30%.

**Every yield divides by ~750.** The 7,435% becomes **~10% a year** — exactly in
line with everything else measured (23% aggregate across Base's busiest pools).

It also explains the last thing I could not explain: **nobody was paying 0.30%.**
They pay four ten-thousandths of a percent, which is why this pool is the busiest
— it is the cheapest. The 49% round-trips were not wash-farming for points; they
are ordinary routing through a near-free venue.

Also confirmed: `factory()` is `0x70fe4a44…`, **not** Uniswap v3's factory on
Base, and `tickSpacing` is 1 — a non-canonical fork, which was the first warning
and should have stopped the calculation before the third measurement, not after.

**Road 14 closed. No euro moved.**

### The lesson, in general form

**A fallback value for a failed measurement is a lie with a number attached.**
If the contract does not answer, measure it or stop — never substitute a
plausible constant. The fallback is worse than an error, because an error
announces itself and a fallback does not.
