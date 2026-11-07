# The decision point — 29 Oct, 00:30

Everything measurable has been measured. What follows is the state and a
recommendation; the choice is Nicolò's.

## What is true, each with a number

| | |
|---|---|
| the trade pays, worldwide | €5,219/day |
| not guarded by repeat actors | €2,958/day |
| capital required | **none** — flash loan at 0.05% |
| cost of a failed attempt | **zero** in a Flashbots bundle |
| awkward collateral sells at | 0.01–0.23% on €200,000 |
| our read speed | 13/second → 150 positions per block |
| borrowers near the edge (<1.20) | 8.6% → ~1,300 of ~15,000 |
| **the window to act** | **12 seconds** |

## Why polling cannot work, finally

A sweep of the 1,300 near-edge positions takes **3.6 minutes** — eighteen
blocks late. Narrowing to the ~50 below 1.02 brings a sweep to four seconds,
inside a block — but we would still learn of the drop **at the end** of the
block and send in the next one. **Always one block behind the winners.**

Being in the same block requires reacting to the oracle update **before** it
is mined. The free channel for that exists (MEV-Share hints, measured: 17
oracle updates in 4 minutes) and failed attempts are free. But using it
means building a real MEV bot.

## My honest recommendation

**I would not build it**, and here is the reasoning rather than the verdict.

- The build is **weeks**, not days: hint stream, pre-computed tip prices per
  position, bundle construction and signing, all reacting inside 12 seconds.
- We would be **the weakest participant** in a field whose other members
  have dedicated infrastructure and years of tuning.
- The €2,958/day "unguarded" figure already shrank 6.6× once when counted by
  actor instead of by contract. It may shrink again under scrutiny.
- Even winning a few percent of it requires beating people at the one thing
  they are optimised for.

What makes me say it out loud rather than keep grinding: **two days of
measurement produced a clear answer, and the answer is that the binding
constraint is twelve seconds of latency against professionals.** That is not
a constraint that work removes — it is one that infrastructure removes, and
infrastructure is the thing we do not have.

## What was gained

The search cost **zero euro**. It produced:

- a contract that compiles clean and cannot lose more than gas
- a replay harness on a local chain copy that killed a plausible plan in one
  evening
- the knowledge that free bundles make speculative attempts costless — a
  genuinely useful fact for any future idea
- sixteen families closed with numbers

**Cash: €52.16, untouched since the first day.**

## The three options

1. **Build it anyway** — weeks of work, low probability, zero money at risk.
2. **Stop here** and take the measurement as the answer.
3. **Look elsewhere**, carrying forward what was learned about free bundles
   and zero-cost attempts.

I lean to 3, and I will not start any of them without Nicolò saying which.

---

## I checked my own conclusion for bias — it holds, and harder

The test that killed the plan used the **five largest** occasions. The
largest are the most contested **by construction**: I chose the sample where
the race is hardest and then concluded the race is hard. That is the
sample-chosen-by-the-subject error, committed inside the decisive test.

Redone on **eight occasions drawn at random** from those above €100 — the
population we would actually compete for:

| premium | window |
|---|---|
| €14,479 | none — same block |
| €4,374 | none — same block |
| €3,299 | none — same block |
| €1,413 | none — same block |
| €412 | none — same block |
| €308 | none — same block |
| €139 | no reading (position already closed) |
| €138 | none — same block |

**Seven of seven readable cases: same block.** Against three of five in the
biased sample, the random one is *worse*, not better.

So the conclusion does not rest on a sample I picked: **every meaningful
liquidation is taken in the block it becomes possible.** Polling is
definitively dead, and the only route left is the same-block one.

The recommendation is unchanged and now better supported.
