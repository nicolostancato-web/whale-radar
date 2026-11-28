# The blind spot, named — 26 Oct

Our own hypothesis generator had produced four dead ideas in a row, so the
question went outside: *not "give us ideas" but "what can we structurally not
see, and what is the shared assumption behind all ten closed families?"*

## Two corrections to things I had said repeatedly

**1. Arithmetic.** I wrote that the pairs effect is "one fifth" of its cost. It
is **one tenth**: 0.0203 against 0.20. Making it viable does not need costs
halved — it needs them **divided by ten**, or the signal multiplied by ten.

**2. The calibration row is not a validation.** I cited it a dozen times — "the
two directions average to exactly minus the cost, so the measurement is sound".
It is an **algebraic identity**: with symmetric linear P&L the gross returns
cancel *always*, so that average comes out right even with look-ahead bias,
impossible fills, or wrong timestamps.

Astra is not alleging those errors exist. The point is that **the check does not
exclude them**, and I used it as though it did. A certification I had issued to
myself.

## The rut, in one sentence

> **There is a large enough, portable return forecast inside public market data
> that an outsider can monetize through fresh, ordinary trades — without any
> advantage in execution, access, financing or inventory.**

All ten closed families change the *predictor* and leave that economic
architecture untouched. We changed "what do I forecast?" ten times and never
changed "why would anyone pay *me*?"

## What the instrument cannot see

- **hourly candles discard event order and executable prices** — whether the
  signal preceded the move, whether a quote existed, whether both legs could
  fill together
- **pooling across markets cancels opposite effects** in different states; a
  zero family centre does not mean every economically defined subgroup is zero
- **a fixed holding period substitutes the clock for the mechanism** — an
  effect realised at a settlement, resolution or flow event is missed
- **charging a fresh round trip to every forecast** hides the value of a signal
  to someone who already holds inventory or must trade anyway
- **treating directional return as the source of payment** excludes being paid
  for a service, for immediacy, for reliability

With the warning that matters: *something can be invisible to the instrument
without being accessible to us.* A sub-second effect is invisible in hourly
candles **and** unavailable at our latency. Finding the blind spot does not
rescue the business case.

## The concrete requirement for the pairs

To be viable, all-in cost must fall below **0.51 basis points per leg** —
fees, spread, slippage and adverse selection included. **An access requirement,
not a signal problem.**
