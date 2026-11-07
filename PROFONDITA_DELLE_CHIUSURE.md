# Depth register — what each closure actually rules out

Nicolò's objection, 25 Oct: *two months to declare crypto unprofitable, and now
a family dies every forty minutes. Are we going fast enough to miss the thing
we are looking for?*

The objection is correct and this file exists so it cannot happen silently.

## Two kinds of "closed", which I had been conflating

**A — Arithmetic.** Valid no matter how many variants were tried, because it is
an identity or a division, not an experiment.

**B — Empirical on N rules.** Says only: *these N rules, on this data, showed
nothing.* It does **not** say the family is empty.

## The register

| # | family | kind | what was actually tested | what it rules out | what it does NOT |
|---|---|---|---|---|---|
| 1 | price patterns, EUR/USD hourly | B | 6 rules × 3 horizons | those 6 | every other price rule |
| 2 | patterns on 19 markets | B | 2 rules × 19 markets, split by time | those 2 | the rest |
| 3 | high frequency, 183k obs | **A** | 6 rules, both directions | **the gross is zero by identity**: mirrored rules averaged to exactly −toll | nothing about non-price inputs |
| 4 | cross-sectional ranking | **A** | 12 tests | **undecidable**: 865 cycles needed, 124 available | whether the effect exists |
| 5 | mechanically-linked pairs | B | 10 pairs × 3 horizons | those 10 | other pairs, other thresholds |
| 6 | funding / positioning | B+ | 2 directions × 3 horizons × 112 markets | this signal, well powered | other positioning measures |
| 7 | attention (volume, trades) | B+ | 2 measures × 3 horizons, split 4 ways | **did not pass its own bar**, 8/8 cells positive | **still open — the only one** |

**A = 2 closures. B = 5 closures.** The five B's are shallow by construction and
are labelled as such from now on. They are *not* proof the family is empty.

## The rule, from now on

1. Every closure declares its **kind** and its **N tested**. A family is never
   "closed" — it is "arithmetically closed" or "N variants tried, nothing
   found".
2. A family with a **B** closure can be reopened at any time, and reopening is
   not a defeat — it is the register working.
3. Before reporting a verdict I state what the test **cannot** see.

## Why speed is not automatically shallowness — and where it is

Much of the two months on crypto went into errors I no longer make: an invented
0.30% fee, look-ahead in the depth estimate, overlapping windows, a sample drawn
from what we happened to collect, a ranking built after the careers were known.
Each cost days. Removing them is real speed, not haste.

But family 1, 2 and 5 were genuinely six-rules-and-move-on. Labelled B, and the
register says so.
