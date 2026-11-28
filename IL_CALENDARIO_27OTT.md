# The calendar: a clean false positive, caught in minutes — 27 Oct

Hours of the day, days of the week, funding settlement windows. Nothing to
predict: the clock is known in advance. 347 markets, 4,460,837 hours.

## What it said at first

Measured in euros per operation, **five day-of-week rules cleared both the
noise and the cost**:

| rule | difference vs random entries |
|---|---|
| Friday | **+0.4830% ± 0.1292** |
| Thursday | **−0.5294% ± 0.1211** |
| Sunday | −0.3299% ± 0.1111 |
| Wednesday | +0.3146% ± 0.1194 |
| Saturday | +0.1572% ± 0.1138 |

Friday's absolute net was +0.3066% — positive after costs. It looked like the
first calendar edge of the project.

## Why it was false

The "26,626 cases" behind Thursday are **347 markets inside the same
Thursday**, and markets move together. The independent unit is **the day**.
Across two years there are about **95 Thursdays**, not 26,626 observations.

Collapsing on the date first — average across markets within a day, then the
statistic across days:

| day | days | mean | vs overall mean |
|---|---|---|---|
| Thursday | 95 | −0.8283% ± 0.7942 | −0.6271% — **in the noise** |
| Friday | 95 | +0.2932% ± 0.9024 | +0.4944% — **in the noise** |
| Wednesday | 95 | +0.2885% ± 0.6350 | +0.4897% — **in the noise** |
| Sunday | 95 | −0.6865% ± 0.7725 | −0.4852% — **in the noise** |

The intervals widen by six to seven times and every one contains zero. The
effect was entirely the miscount.

## And a correction to this morning's yardstick

I wrote that "a class-test difference of 2.2 is inside the noise". That
number is in **t-units, which grow with the square root of the sample size**.
The test it came from had a few thousand observations; this one has 185,000
per rule, where the same economic effect produces a far larger t. **The
yardstick does not transfer between designs with different n.**

What transfers is the **percentage per operation**, compared against the cost.
The memory has been corrected accordingly.

## The thing worth keeping

This is the third time today the same family of error appeared — a sample
that is a sample of us, rows counted as cases. Each time it was caught in
minutes, and this time **before the verdict was written**, not after. The
error is not gone; the time to recognise it is collapsing, which is the only
measure of learning that means anything here.
