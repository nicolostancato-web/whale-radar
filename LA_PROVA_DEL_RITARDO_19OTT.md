# Following a buy, post-graduation: the first numbers (19 Oct)

The pre-graduation phase was closed. The founder's new direction: the **post-graduation** market
on Robinhood Chain, where the market is continuous and skilled traders are more likely to
operate — and the question is whether their wallets can be copied.

Both external reviewers said the same thing before any code was written: do **not** build the
wallet table first. Run one measurement that can kill the thesis in a day, using only the swaps
of the graduated pools and no wallet data at all. Copying means arriving after; the buyer's own
trade has already moved the price; so the only thing a follower can capture is **what is left
after that trade**. If that is less than the cost of a round trip, no wallet on earth makes
copying pay.

## Coverage, rebuilt from the chain

Our archive believed there were 847 Pons graduates. Read directly from the chain — every
`Initialize` of the v4 PoolManager carrying the Pons hook — there are **10,332**, of which
**5,098 are quoted in the native coin**, spanning 10 Aug to today.

**Our previous post-graduation dataset covered 8% of the universe.** Every figure measured on it
was a sample of how we collected, not of the market.

## The measurement (on 3,123 of the 5,098 pools; collection still running)

Entry at the price after someone's buy, plus our real latency of 11 blocks (one second). Exit
at a **sell** print, because a seller hits the bid — mixing the two sides of the book
manufactures a fake 5 points. Collapsed to the coin, not to the row.

| exit after | return per coin |
|---|---|
| immediately | **-6.76% ± 0.33** |
| **+11 blocks (our one second)** | **-7.39% ± 0.37** |
| +1 minute | -13.01% ± 0.89 |
| +5 minutes | -20.23% ± 1.41 |
| +1 hour | -37.84% ± 2.39 |

Only **1% of coins** have a positive average. No slice by age rescues it.

## The one positive cell, and what it was

Weighted by trade size, one of sixteen cells came out positive: buys above EUR 300 within the
first 10 seconds after graduation, **+5.49%** across 2,322 coins. Stressed immediately:

| | |
|---|---|
| weighted return | **+5.40%** |
| plain, unweighted return | **-5.16%** |
| median | -4.64% |
| in profit | 35% |
| **the 3 best coins' share of the weighted gain** | **100%** |
| **removing those 3 coins (8.2% of the money)** | **-0.01%** |

Three coins out of 2,329. The cell is not a strategy, it is a weighting artefact — the same
shape as every other number this project has had to throw away.

## Two mistakes of mine, both caught and written down

**Appending to a compressed file.** An interruption makes the whole archive unreadable. This
lesson was already in memory and I repeated it anyway; the collector now writes plain text and
compresses only when closed.

**Mixing the two sides of the book.** Entering at a buy print and exiting at whatever print came
next understates the cost by about 5 points on these pools. Entry is now a buy, exit is a sell.

## Status

Collection at 61%. The complete figure, the calendar split at 29 September, and the verdict on
whether the wallet database gets built come when it finishes.

---

# The complete sample, and the number that matters

Collection finished: **5,096 graduated pools, 17.0 million swaps**, zero rejections.

**A — following a buy at our real latency, exiting immediately on a sell print**

| | |
|---|---|
| coins | 5,094 |
| return | **-6.87% ± 0.20** |
| median | -4.29% |
| coins with a positive average | **0%** |

**B — following every buy, target 2x, stop -50%, both declared in advance**

| | |
|---|---|
| operations | 6,422,415 on 5,094 coins |
| **that double** | **29.36%** |
| that stop out | 61.49% |
| return per operation | **-2.22%** |

## This is not "there is nothing here". It is a bar.

The founder's expectation was that this market is made of large multiples, and that is correct:
**three followed buys in ten double.** The market is not flat. The arithmetic is simply even:
29.36% × +100% against 61.49% × -50% is a coin toss, and the round trip costs about 6% on top.

So the question for the wallet phase is no longer "does an edge exist" but a measurable
threshold:

| round-trip cost | doubles needed | we have |
|---|---|---|
| 0% | 33.3% | 29.36% |
| 3% | 35.3% | 29.36% |
| **6% (realistic)** | **37.3%** | **29.36%** |

**A wallet worth copying is one whose followed buys double 37% of the time instead of 29%.**
Eight points of selection. That is the target the wallet database is being built to test, and
knowing it before building is worth more than any ranking produced without it.

Supporting facts: the fixed-horizon return is negative in every ten-day period since August
(-4.4% to -7.9%), so the end of the gas subsidy on 29 September changes nothing; and the single
positive cell found under size weighting (large buys in the first 10 seconds, +5.4%) was **three
coins out of 2,329** — removing them leaves -0.01%.
