# The premium, measured instead of assumed — 28 Oct

Every euro figure so far used a **5% liquidation bonus**, taken from Aave's
documented range. The event itself contains both sides — debt repaid and
collateral seized — so the premium can be **computed**, not assumed. An
assumed constant is an error waiting (the 0.30% fee that was never read from
the contract cost a factor of 750).

## 30 valuable occasions

| premium, measured | |
|---|---|
| **median** | **3.76%** |
| lower quartile | 2.19% |
| upper quartile | 4.50% |
| maximum | 12.93% |
| minimum | **−0.03%** — a liquidation done at a loss |

My 5% assumption was **a third too generous**, and it is now replaced by a
measured value with its spread.

## In euros

| | |
|---|---|
| three largest | €17,451 · €9,527 · €6,532 |
| then | €329 · €151 · … |
| median | **€7.76** |
| total over 30 occasions | €34,325 |

**Three events are almost the whole sum.** The daily figure remains
unquotable until coverage grows — at 9% of the 60 days, dividing would give
~€6,300/day, and that number rests on three observations.

## Collection status

The gentle collector (5 windows per run, stop at first refusal, state saved
each step) is at **8 of 90 windows**. It burned itself out once by hammering
88 windows in a row; the pace now holds without refusals.

---

## Who wins — 60 events, 14% coverage

| | |
|---|---|
| distinct liquidators | **29 of 60 events** |
| busiest | 13.3% |
| second | 10.0% |

Not five professionals — **a crowd**. That cuts both ways: the door is open,
and the share is small.

**Large occasions** (premium over €500): only 5 in 60 events, won by **three
different addresses**:

| address | occasions | total |
|---|---|---|
| 0x00c1f6d6… | 3 | €31,555 |
| 0x963feb54… | 1 | €1,493 |
| 0x271e33ab… | 1 | €913 |

Even the large ones are not monopolised — though with five cases nothing is
settled.

## The shape forming

An **open and crowded** trade, where the money sits in a few rare strikes
that do not always go to the same hands. The earlier guess of "one of the top
five takes €100/day" was built on six events and is wrong about the number of
players: 29 appear in a 14% sample.
