# The first candidate with no gate — 28 Oct

Sixteen families. Fifteen ended the same way: nothing is paid, or entry costs
capital. This one ends differently, and it deserves care rather than
enthusiasm.

## Why liquidations have no gate

With a **flash loan** you liquidate without putting up a euro: borrow, repay
someone else's debt, take the collateral premium, return the loan — all in
one transaction. If it is not profitable it does not execute. Only gas is at
risk, and gas on Ethereum is now **0.064 gwei** (verified against the current
base fee, because a number that surprising must be checked before it is used).

## It is not monopolised

| Aave v3 on Ethereum, 2 days | |
|---|---|
| distinct liquidators | **5 out of 6 events** |
| share of the largest | 33% |

On Base the same measurement gave 2 events, both to one address — but Base
was chosen because I had the connection there, not because it is where
liquidations happen. The mainnet picture is the real one.

## And the premium is not competed away

The fear was that the premium goes to the validator in the block-space
auction. Measured against the MEV relays' public payment data:

| block | collateral seized | premium ~5% | **paid to validator, whole block** |
|---|---|---|---|
| 26279102 | €2,515 | €125 | €100.62 |
| **26286758** | **€12,297** | **€615** | **€68.60** |

On the large one the validator received €68 for the **entire block**, so at
least **€546 stayed with the liquidator**. (The relay figure covers the whole
block, so it is a ceiling — which is what makes the conclusion safe.)

## The size, and three warnings

Adjusting the 3-day observation for 45% window coverage: roughly **€450-500
per day worldwide** on Aave v3 Ethereum, split among a handful of actors —
on the order of **€100/day** for one of the top five.

That is **ten times the €10/day ceiling** of the entire trading space, and it
needs engineering rather than capital.

The warnings, stated before anyone gets excited:

1. **Three quiet days.** Liquidations arrive in waves — they multiply during
   a crash and vanish in calm. This sample may understate or overstate badly.
2. **45% coverage.** The adjustment is crude.
3. **Entering adds a competitor.** The share is not simply there for the
   taking.

## What happens next

Not a conclusion — the first candidate worth a **forward study**. An
accumulator starts now, because the right number appears over weeks, not over
three days. Aave is also one protocol among several (Morpho, Compound, Spark,
Fluid), so the pot measured here is a floor on the trade, not its size.

---

## Is it a millisecond race? ~~Apparently not~~ — WITHDRAWN, see below

The obvious objection to us competing: winning a liquidation is a latency war
against professional bots, and our infrastructure is public RPCs that drop
**55% of requests**. You do not win a millisecond race with that.

There is a cheap and decisive test. A professional bundle lands at the **top
of the block** (index 0-2) with an aggressive bid, because that is how the
race is won. Ordinary transactions land scattered.

| protocol | position in block | gas price |
|---|---|---|
| aave_v3 | **36** of 314 | 0.782 gwei |
| aave_v3 | **42** of 108 | 0.099 gwei |
| spark | **51** of 268 | 0.056 gwei |

**None at the top. Median 19% into the block, ordinary gas prices.**

These are not bundles winning a latency auction — they are normal
transactions. Which suggests the liquidation is won not by being
**fastest** but by **noticing**, and noticing is a race that can be run on
public infrastructure.

**Three events is a small sample**, and the large profitable ones may behave
differently from the small ones. The accumulator will settle it. But this is
the first obstacle I had assumed was fatal that turns out not to be there.

## Accumulator status

2,208 blocks covered, 0% failed, 3 liquidations → ~10/day. The rate has moved
8 → 10.5 → 9.8 across runs, which is why three days of coverage are required
before quoting a number.

---

## WITHDRAWN, two hours later: the position test has no power

The conclusion above — "not a latency race, because liquidations are not at
the top of the block" — **does not hold, and I published it.**

Position in a block measures competition only if blocks are **full**. They
are not:

| 20 recent Ethereum blocks | |
|---|---|
| fullness, median | **41%** (min 13%, max 99%) |
| base fee, median | **0.0418 gwei** |

At 41% full, anything gets in anywhere. Position says nothing about who won a
race. And both large liquidations paid **exactly the base fee, zero tip** —
one landed at position 1, the other at position 42. That spread, with
identical zero tips, is the signature of **no contention for block space**,
not of an open race.

So: the feasibility question is **open again**. Whether we could win a
liquidation is unmeasured.

## The measurement that would settle it

How long between a position becoming liquidatable and being liquidated. The
trigger is a price oracle update (Chainlink `AnswerUpdated`, public). If the
liquidation lands in the **same block** as the update that made it possible,
it is a bot racing the oracle and we cannot compete. If minutes pass, there
is room.

That is the next measurement, and it replaces the one just withdrawn.

---

## What one occasion is worth — 28 Oct

Counting by **transaction**, not by event (one transaction liquidated eight
positions; counting those as eight inflated the rate from 11 to 30 a day):

| occasion | positions | collateral | net after gas |
|---|---|---|---|
| 0x38ca2a07… | 1 | €12,340 | **+€616.81** |
| 0xecd28001… | 1 | €45 | +€1.17 |
| 0x4bf676b0… | 1 | €2 | +€0.02 |
| 0xbb95f74f… | **8** | €4 | **+€0.01** |

**Median: 59 cents.**

One occasion in four is worth anything, and it is worth €617. The rest are
dust — including the eight-position transaction, which nets **one cent** and
is housekeeping, not profit.

So "~11 occasions a day" is true and nearly useless: ten of them are dust.
What matters is how often the **large** ones arrive, and **one** has been
observed. A frequency cannot be estimated from one event.

This is the same shape as two lessons already paid for: quantity is not
opportunity, and a mean driven by a single case is not a mean.

## Also worth noting

Gas makes the small ones worthless (€0.01–1.17 net). Whoever is clearing
dust is not doing it for money — which means the competitors visible in the
"5 distinct liquidators" count are not necessarily competing for the
occasions that pay.

**The accumulator continues. No number is quotable until roughly ten large
occasions have been seen.**
