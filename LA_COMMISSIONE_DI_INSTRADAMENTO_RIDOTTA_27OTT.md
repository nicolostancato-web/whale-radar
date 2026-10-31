# The routing fee, divided by seven — 27 Oct

The last open architecture was "the app that collects a routing fee": users
swap through your interface, your address receives a cut, no account and no
minimum. The first measurement said **47-68% of router transactions pay such
a fee**. That number was wrong, and the error was mine.

## The defect

`campiona_le_commissioni.py` appended one row **per fee transfer** and then
divided by the number of **transactions**. Numerator and denominator were
different units, so the "share" could exceed 100% and never meant anything.

A fee-paying transaction carries **6.7 fee transfers on average**. That is
the whole factor of seven.

## How it was caught, and this is the part worth keeping

Not by re-reading the code. A **second sampler**, written for a different
question (which niche the fee-collecting apps serve), counted the same
quantity by a different route and said **4.8%** where the first said 33%.
Two counters of one quantity, disagreeing, is the only alarm that fires on a
unit error — the code reads correctly in isolation, and every individual
number inside it is right.

After the fix the two agree: **5%** against 4.8%.

## What it does to the product

| | first estimate | measured |
|---|---|---|
| share of router transactions paying a fee | 47-68% | **~5%** |
| median rate when paid | 0.33% | 0.467% (unchanged, the rate was per-withdrawal and that unit was correct) |
| plausible revenue at the volume previously assumed | ~€500/day | **~€50/day** |

€50/day is not nothing, but it is no longer an architecture that changes the
problem — and it still assumes you have the users, which is the part nobody
has measured and the part that is actually hard.

**The architecture is not closed, but it is demoted:** the prize is a seventh
of what justified looking at it.
