# Watching is feasible — 28 Oct

The open question was detection: can we notice a liquidatable position before
the other 29 participants, using free public infrastructure?

## The speed of watching

Aave exposes `getUserAccountData(address)`, which returns the **health
factor** — below 1 the position can be liquidated. Measured against a free
public node:

| | |
|---|---|
| read calls per second | **6** |
| positions per block (12s) | **~72** |
| positions per minute | ~362 |

Watching is possible **if the list to watch is a few hundred positions, not
tens of thousands**. That list is buildable: a slow sweep each hour to find
everything near the threshold, then only the shortlist checked every block.

## What is sitting there right now

Of 133 previously-liquidated addresses, **23 still carry open debt**:

| address | debt | health |
|---|---|---|
| 0x7a057501… | **$25,314** | **1.000** |
| 0x69c0bb9a… | $7,505 | 1.038 |
| **0x40e93a52…** | **$116,340,051** | 1.051 |
| 0x26e449a3… | $671,159 | 1.086 |

Two things matter here.

**One position is sitting at health exactly 1.000 with $25,314 of debt and
nobody has taken it.** Either it is not actually profitable to take, or the
competition is not instantaneous — and both readings are useful, because the
second is the one I assumed was impossible.

**A $116 million position sits at 1.051.** That is where €36,000 premiums
come from: a single large borrower slipping under.

## A bug worth naming

The first run reported "0 responses" and would have read as "public nodes
cannot do this". The cause was mine: I checked for a reply of at least 396
characters when the correct length is 386 — six words plus the prefix. **A
wrong length check discarded every valid answer**, and the conclusion would
have been the opposite of the truth.

---

## Correction: the untouched position was simply not liquidatable

I wrote that a position sitting at health 1.000 with $25,314 of debt, taken
by nobody, suggested "the competition is not instantaneous". Reading the
value with full precision:

| address | collateral | debt | health, full precision |
|---|---|---|---|
| 0x7a057501… | $26,501 | $25,176 | **1.000006062** |
| 0x40e93a52… | $127,967,490 | $115,706,899 | 1.050664365 |
| 0x26e449a3… | $862,926 | $671,163 | 1.080002983 |

**Above 1. Not liquidatable.** The "1.000" was a rounded display, and the
explanation that saved my hypothesis — the one that came to mind first — was
false. The boring one was right.

## And it sharpens the real question

That position needs a **0.001%** fall in collateral value to tip. It is
balanced on the edge, which means when it goes, it goes instantly, and the
race at that instant **does exist**. I closed the speed question too quickly
in my own favour, and it is open again.

The $116 million position needs a **4.82%** fall. That is where €36,000
premiums come from, waiting.

## What must be measured next

For a liquidation that did happen: how many blocks after the oracle update of
**its own collateral asset** — not ETH/USD, which may not be the trigger. The
earlier 44–170 block delays were measured against the wrong feed and prove
less than I claimed.
