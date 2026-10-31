# The constraint that reshapes the search — 25 Oct

## What was tested

A genuinely different hypothesis class: not "does this market rise after a
pattern" but **"among many markets, do the top-ranked beat the bottom-ranked"**
— long the top, short the bottom, so the common tide cancels by construction
(the trap that fooled me on silver).

- 18 commodities: reversal consistently positive (+0.26% to +2.62% per cycle),
  **all 12 tests not demonstrated**, intervals ±1.1% to ±4.9%
- 99 large-cap stocks: point estimates small and **inconsistent in sign**,
  all 12 not demonstrated, intervals ±0.79% to ±3.97%

The two directions come out exactly mirrored, which is the check that the code
does what it claims.

## The structural finding, which matters more than the result

Every one of these tests has **37 to 124 cycles**. With a per-cycle dispersion
around 4.5%, demonstrating a 0.3%-per-cycle effect needs:

> n ≈ (1.96 × 4.5 / 0.3)² ≈ **865 cycles** — about **seventy years** of monthly
> rebalancing.

**Any strategy that rebalances about monthly is undemonstrable with the history
that exists.** Not "does not work" — *cannot be known*, even if correct.

This is the lesson of the 200-position forward test that could not decide,
generalised. It yields a filter that applies from here on:

> **Only pursue strategies that generate thousands of independent observations**
> — high frequency, or many simultaneous positions on uncorrelated things.
> Everything else is unsellable by construction, because we could never
> distinguish it from chance before risking money on it.

It also explains, in hindsight, why the memecoins were the right place to look
even though the answer was no: there we had 5,139 observations.

## Practical consequence

Before testing any future candidate, compute **the number of observations it can
produce** and the n required for its plausible effect size. If the required n
exceeds what the data can give, **do not run the test** — design a different
strategy or a different measurement.
