# Nobody is paying to win — 28 Oct

If large liquidations were contested, winners would bid for block space. The
data says they do not.

| premium band | occasions | median premium | median gas cost | cost / premium |
|---|---|---|---|---|
| **over €5,000** | 8 | €17,208 | **€4.19** | **0.02%** |
| €1,000–5,000 | 19 | €1,701 | €1.69 | 0.10% |
| €100–1,000 | 24 | €234 | €0.89 | 0.38% |
| €1–100 | 60 | €11 | €0.44 | 3.92% |

Every occasion above €5,000, one by one:

| premium | gas cost | gas price | kept |
|---|---|---|---|
| **€98,150** | **€0.20** | 0.064 gwei | **100.0%** |
| €79,010 | €15.12 | 1.202 gwei | 100.0% |
| €52,085 | €12.53 | 1.253 gwei | 100.0% |
| €17,817 | €9.40 | 2.504 gwei | 99.9% |
| €16,600 | €3.95 | 2.179 gwei | 100.0% |
| €13,421 | €4.42 | 1.105 gwei | 100.0% |
| €12,103 | €0.44 | 0.163 gwei | 100.0% |
| €7,651 | €0.21 | 0.127 gwei | 100.0% |

**There is no auction.** Winners keep essentially the whole premium, and the
one who took €98,150 paid twenty cents.

(This measures priority fees. Direct validator payments were checked
separately on two blocks via the MEV relays: €68 and €100 for entire blocks —
consistent with no large hidden bid.)

## The explanation that would kill it, and must be tested first

If the big strikes are made by **parties related to the position** — the
borrower limiting their own damage, or a lender protecting itself — then this
is not an open race won by whoever notices, and the real open market is only
the dust. **Twenty different winners across twenty-four large occasions makes
that plausible**: professionals repeat, related parties appear once.

Test: look for a relationship between liquidator and liquidated user —
shared funder, prior transactions between them, co-activity. If the big ones
are related-party, the candidate collapses to the dust tier.

This is the most consequential open question, and it gets tested before
anything optimistic is said out loud.

---

## The related-party hypothesis is dead — tested, 28 Oct

Of the 16 largest occasions:

| | |
|---|---|
| liquidator is a **contract** | **16 of 16** |
| self-liquidations | **0** |
| liquidator appears more than once | **10 of 16** (one 20×, one 9×, one 6×) |

These are professional bots, not borrowers limiting their damage. The market
is genuinely open — and the optimistic reading survives its first serious
test, which is rare enough to note.

## But it reframes the problem precisely

Professionals compete, and **they pay no tip because none is needed**: blocks
are 41% full at 0.05 gwei, so there is room for everyone. Nobody has to
outbid anybody.

Competition is therefore **entirely in noticing first**, and that is where we
are structurally slow: dedicated nodes against our **6 reads per second** on
public infrastructure. We would be the twenty-first bot, and the slowest.

## The question that is left, and it is not hopeless

**Are there occasions the professionals systematically miss?** Candidates:
unusual collateral assets, smaller protocols, newly listed markets, positions
whose trigger is not a price move. A slow entrant cannot win a race, but can
win where nobody is racing.

That is the next measurement: cross the occasions against which liquidator
took them, and look for assets or protocols where the repeat players are
absent.
