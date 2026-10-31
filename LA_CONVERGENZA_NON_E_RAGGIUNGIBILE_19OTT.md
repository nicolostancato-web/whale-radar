# The leaders converge, but you cannot arrive in time (19 Oct)

## What was being tested

Wallet `0xc54d3914f91f` buys only 2% of the coins and makes +24%. One of his two visible
filters is that he follows a set of **leader addresses**. Generalised: 88 leaders were
selected using only the first half of the period, then checked on the unseen second half.

The filter is real. On 784 untouched coins it adds **+5.57 points**, and the win rate rises
with how many leaders converge on the same coin: 1 leader 23%, 3 leaders 35%, 4+ leaders 46%.

## The measurement that closes it

On the 100 unseen coins where at least 3 leaders converge, the third leader arrives a
**median 1.9 seconds after birth** (quartiles 1.4s and 3.2s). The question is not whether
the signal exists, it is what is left of it once we have seen it:

| if we enter          | coins | return  | ±    | in profit |
|----------------------|-------|---------|------|-----------|
| at the same instant  | 100   | +11.50% | 14.2 | 42%       |
| 1 second later       | 100   |  +1.25% | 12.6 | 38%       |
| 2 seconds later      | 100   |  +0.68% | 12.1 | 37%       |
| 5 seconds later      | 100   |  -0.61% | 11.6 | 38%       |

Costs (1.06 round trip) are already inside those numbers.

Our measured send latency is about **1 second**, and that is before detecting the third
leader's transaction. So the honest line for us is the second one or worse: +1.25% ± 12.6,
an interval that contains zero. Nothing to cash.

## The lesson, written in positive form

A selection signal has to be judged **from the price at the moment we could actually place
the order**, never from the price at birth. The whole +11.50% of this filter lives inside the
first second after the signal becomes visible, which is exactly the second we cannot buy in.

This is the same family as the H4 pattern and the diploma rule: the edge was in the part of
the timeline we do not own.

## Status of the pre-diploma phase

Strategies measured and closed so far: post-diploma trading, the 50-5 family, stop/target on
corrected prices, entry thresholds, all four winner profiles (creator, snipers, sandwich,
selectors), "buy every graduate", and now leader convergence.

Cash untouched: EUR 52.16, machine off, floor at EUR 56.

---

# Same night: the only latency-proof filter, and why it also fails

If the signal cannot be a reaction (we are one second too slow for those), it has to be
something **readable at birth**. There are exactly two such things: the creator tax, already
in hand, and the **identity of the creator**, which sits in topic[3] of `TokenLaunched` and had
never been extracted. `agents/creatori.py` now pulls all **701,019 launches** of the factory
(free, public RPC, address filter). 9,005 of our measured coins have a known creator.

Entering at 2s, target 3x, 11 minutes, cost 1.06, verified on the unseen second half:

| rule                             | coins | return  | ±    | in profit |
|----------------------------------|-------|---------|------|-----------|
| all                              | 4503  |  -2.80% | 1.2  | 14%       |
| zero creator tax                 |  944  |  -2.82% | 3.4  | 17%       |
| creator's first launch           | 3372  |  -2.39% | 1.5  | 15%       |
| creator with 2+ prior launches   |  874  |  -4.12% | 2.3  | 10%       |
| creator with 10+ prior launches  |  455  |  -4.56% | 3.4  | 12%       |
| creator whose past coins made >20% | 50  | +10.39% | 15.7 | 30%       |

The last line looks alive. It is not, and the check that kills it is the one that has killed
everything else — **look at the half you did not look at**:

| rule (3+ prior, past return >20%) | first half | unseen half |
|---|---|---|
| 3+ prior, >20%  | **-6.15%** (26) | +10.39% (50) |
| 3+ prior, >0%   | **-10.84%** (57) | -1.78% (125) |
| 2+ prior, >20%  | **-10.08%** (36) | +8.67% (61) |
| 5+ prior, >20%  | **-15.49%** (12) | +13.04% (37) |

Every variant is **negative on the first half and positive on the second**. A rule whose sign
flips between the two halves of the same period is not an edge, it is the market changing.

Three further checks on the surviving cell: the 50 coins come from only **9 distinct creators**
(so they are 9 cases, not 50), the **median is -11.32%** against a mean of +10.39% carried by a
single +183% coin, and removing the three best leaves **-0.62%**. A random group of 50 coins
does as well 2.15% of the time, which is not enough once you count the 8 rules tried.

**Closed.** Both the reaction signal and the only birth-time signal are gone in the same night.

---

# A free label we never had: which curves are quoted in the native coin

Asking "is being the creator a business?" produced an absurd answer first: on 400 launches
drawn at random from the whole factory, the mean 2% creator tax came out at **EUR 20,016 per
launch**, with one curve declaring EUR 278 million of volume across **10 buys**. The guard held
— the extremes were checked before the number was spoken — and the cause was immediate: only
**6 of those 400 launches** were in our hand-built list of native-quoted curves. Dividing every
amount by 1e18 is meaningless for a curve quoted in some other token.

The fix turned out to be free. The **first data field of `TokenLaunched` is the quote token**:
zero means native. `agents/creatori.py` now records it for every launch:

- factory launches: **701,036**
- native-quoted: **424,571 (60.6%)**
- our measured set covers **2.3%** of them

It also audits our own list: **1,140 of the 9,823 curves we have been measuring (11.6%) are
quoted in an ERC20, not the native coin**. That matters for every figure in euros — and for
nothing else, because a return is a ratio of two prices and the decimals cancel:

| set | coins | return |
|---|---|---|
| everything we were measuring | 9053 | -3.99% ± 0.9 |
| native confirmed by the event | 7980 | -4.07% ± 0.9 |
| the 1,140 with an ERC20 quote | 1073 | -3.43% ± 3.0 |

No past return measurement is damaged. Every past statement in euros about volume or creator
revenue is, and the honest version has to be rebuilt on the 424,571 native launches.

---

# And the pre-registered forward test, now caught up, closes negative

`prova_tassa_zero.py` was frozen before it ever ran: zero creator tax only, enter 4 seconds
after birth, target 3x, 10 minute deadline, cost 1.02, no parameter touched since. It had
fallen about 16 hours behind the chain; it is now at the head.

- coins seen: **1,076** — 764 rejected by the filter, 150 closed on the deadline, 3 on target
- real positions: **153**
- return: **-6.77% ± 5.6**, median **-4.32%**, in profit **12%**
- removing the single best (+194%): **-8.09%**

The interval does not contain zero. This is the strongest verdict of the whole pre-diploma
phase, because nothing about it was chosen after seeing the data.
