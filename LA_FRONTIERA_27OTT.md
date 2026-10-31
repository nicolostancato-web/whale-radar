# The frontier: what the whole space could pay, per day — 27 Oct

Nine roads closed with the same sentence — *not the signal, the capacity*. A
sentence repeated nine times should become a number. Every measured road,
converted into the one comparable unit: **euros per day**.

## The correct formula, after fixing my own error

The first version multiplied the edge by the number of opportunities per day
and produced €124/day for one road. That is wrong: it assumed €52 could be in
sixteen places at once. The binding constraint is **how often the cash turns
over**:

```
EUR/day = min(cash, capacity per operation) × edge% × turns per day
turns per day = min(opportunities per day, 24 / hours held)
```

## The result

| road | turns/day | €/day on €52 | €/day on €5,000 |
|---|---|---|---|
| Pons: buy every graduate | 0.33 | 2.60 | 10.00 |
| sell the debut | 0.33 | 1.05 | 1.05 |
| volume spike | 2.00 | 0.23 | 4.40 |
| cross-venue arbitrage | 1.30 | 0.00 | 0.00 |
| same pair, two pools | 48.00 | **0.00** | **0.00** |
| funding spread | continuous | 0.01 | 0.82 |

**And every road in this table has already failed out of sample.** The numbers
say what they would have paid *if they had been true*.

## The road the frontier re-opened, and then closed properly

"Same pair, two pools" first came out at **€15.72/day even on €52**, because
48 small turns a day add up where a single one looks like nothing — a real
blind spot in how I had dismissed it an hour earlier.

Then the decisive check: two pools of one pair may legitimately differ by up
to the **sum of their fees** with no arbitrage existing at all. Reading the
real fees from each contract (never assuming them — that error has been paid
for): **12 pairs out of 12 sit inside the band**, and most show a difference
of 0.000%. The 1.31% that started it was one pool whose last price was stale
across six blocks.

So the row is zero, and the road is closed for the right reason.

## What the frontier actually says

With €52, the best road in the entire measured space — **assuming the failed
ones had worked** — pays about **€2.60 a day**. With €5,000, about €10.

That is the shape of the whole space, in one number. It is not an argument
about whether an edge exists; it is the ceiling on what an edge of the size
anyone has ever measured here could pay at this capital.
