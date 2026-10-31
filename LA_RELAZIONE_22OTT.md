# The relationship that explains three months (22 Oct)

Three chains, six dead positives, and every time the beautiful number sat where a large share
of positions had nobody to sell to. Measured directly on 18 pump.fun tokens with complete
trade histories:

| share of positions stuck | tokens | calibration | return IF closed | return counting stuck at zero |
|---|---|---|---|---|
| under 10% | 7 | -4.25% | **-4.31%** | **-4.31%** |
| 10-30% | 3 | -3.63% | +10.71% | +3.63% |
| over 50% | 6 | -5.83% | **+18.80%** | **-100.00%** |

Correlation between stuck share and apparent return: **+0.45**.

Read the last row twice. On tokens where more than half the positions cannot be sold, the
strategy returns **+18.80%** if you count only the ones that closed, and **-100%** if you count
the rest. And on tokens where you can always exit, the return is **-4.31%** — exactly the toll,
flat, as on Robinhood and Base.

## What it means

**The apparent profit in these markets is the unsellable inventory.** A price that rises while
nobody sells is a price with no real bid — the side that would pull it down is missing. Look
only at those who got out and you see a market that explodes. Count those left holding and you
see the truth.

This explains six false positives across three chains in one line, including the one that
replicated across two unseen periods: every time the attractive number came from survivors.

## The rule from here

The test for any market is no longer "what does it return", it is **"what does it return, and
how many of the positions producing that number could actually be closed"**.

Discarding positions with no exit is the error, not the caution. They are counted at -100%, or
at the last observed price with that stated, and the stuck share is always reported.
