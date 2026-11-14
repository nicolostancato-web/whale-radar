# The door, verified on-chain — 24 Oct

Grok read the published rates. The project's rule is that documentation is not
evidence, so the mechanism was checked against reality.

## Measured on Base, 25 minutes, Uniswap Universal Router

- 706 transactions went through the router
- 70 receipts read in full
- **33 of them (47%) carry an app fee** — a transfer of part of the swap to an
  address that is not the pool, not the router and not the trader
- **median fee kept: 0.206%** (range 0.041% – 0.825%)
- at least six distinct recipients, i.e. six different apps collecting

Three things follow, all measured rather than assumed:

1. **The door is open in practice**, not only in the documentation.
2. **Users already accept it** — nearly one router transaction in two pays an
   app fee.
3. **The market rate for the service is ~0.2%**, not the 1% I hoped for and not
   the 0.15% I had assumed.

## The last number measurement can give

> **EUR 500/day = EUR 243,000 of daily volume through something of ours**, at
> the rate the market actually pays.

For comparison, the same EUR 500/day stated the other ways:

| as | requires |
|---|---|
| a return on EUR 52 | 962% per day |
| capital at the best measured yield | EUR 787,000 |
| **volume through an app at the measured 0.206%** | **EUR 243,000/day** |

## Where measurement stops

The question is no longer *whether a way exists*. It exists, it is open, it
needs no capital, no latency and nobody's permission, and six apps are using it
today. The question is what to build that carries EUR 243,000 a day — and that
is not a question about chains.

---

## Confirmed on a 3× larger sample

200 receipts over 3 hours, **zero failed reads**:

| | first pass (70 receipts) | **now (200, 3h)** |
|---|---|---|
| router transactions carrying an app fee | 47% | **68%** |
| median fee kept | 0.206% | **0.204%** |
| distinct apps collecting | 6 | **34** |

The rate reproduces to within a ten-thousandth. The quartiles are **0.090% and
0.755%**, so apps choose anywhere in that range rather than facing one imposed
price.

The new fact is the third row: not six oddities but **thirty-four applications
doing this today on one chain**. It is standard practice, not a trick.

> **EUR 500/day = EUR 244,799 of daily volume**, confirmed.

---

## WITHDRAWN the same evening: the measurement is not reproducible

Same script, same parameters, a few hours later:

| | afternoon | evening |
|---|---|---|
| transactions carrying a fee | 136 of 200 (**68%**) | **8 of 200 (4%)** |
| median fee | 0.204% | **0.631%** |
| distinct apps | 34 | **6** |

A swing that size over four hours is not the market — it is **an unstable
measurement**. Two snapshots of the same phenomenon this far apart means neither
is a fact.

**Withdrawn as measurements: 0.204%, 68%, and "34 apps".** They were not wrong
through an identifiable coding error, which would be easier; they were false in
their precision, which is worse, because they looked solid. The earlier claim
that the rate "reproduces to within a ten-thousandth" was the artefact of
comparing two overlapping samples from the same hours.

### What still stands

- **App fees are real**: seen in both samples, 136 times and 8 times. The
  mechanism exists; it is not an artefact.
- **The published rates are independent of my measurement**: Zora 0.20%,
  LI.FI 0.25%, Rainbow 0.85%, Uniswap 0%.
- Both of my discordant samples fall **inside** that published range, which is
  the only confirmation I can honestly claim.

So the door stays open and the price is of the order of **0.2–0.9%**. What I do
not have is the decimal, and I had pretended to.

### The lesson

**One snapshot of heterogeneous flow is not a rate.** A rate requires repeated
samples at different times, and the spread between them reported alongside the
central value. A second sample taken four hours later would have cost ten
minutes and would have prevented the claim.
