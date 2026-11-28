# The rate, replicated — 25 Oct

Six samples, six distinct hours, 120 receipts each, randomly drawn inside the
window (not oldest-first, which was yesterday's methodological fault).

| | median | range across samples |
|---|---|---|
| **fee an app keeps, when charged** | **0.295%** | **0.198% – 0.500%** |
| share of router transactions paying one | 23% | 10% – 54% |

Per-sample: 0.334 / 0.343 / 0.500 / 0.227 / 0.255 / 0.198 (%), at frequencies
23 / 10 / 23 / 47 / 54 / 12 (%).

## EUR 500/day, with its spread

| rate | daily volume needed |
|---|---|
| 0.500% (favourable end) | **EUR 100,000** |
| **0.295% (central)** | **EUR 169,000** |
| 0.198% (unfavourable end) | EUR 253,000 |

The true figure is **better** than yesterday's claim: I had stated 0.204% and
EUR 243,000; the replicated median is 0.295% and EUR 169,000.

## What this cost and what it bought

Yesterday: a precise number that was false (0.204%, "reproduces to within a
ten-thousandth" — an artefact of two overlapping samples taken oldest-first
from the same hours). Today: an imprecise number that is true.

The first would have been the basis of a wrong decision. The second is a basis.

Two fixes are now in the code rather than in my memory:
- the sampler draws **randomly** inside its window;
- it **refuses to print a rate** until six samples across four distinct hours
  exist, and always prints the range beside the median.

It caught me twice in one day — once when I called a two-sample spread "very
stable", and once when the third sample widened it by half.
