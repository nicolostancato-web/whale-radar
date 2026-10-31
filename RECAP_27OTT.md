# 27 October, in one page

## Is there a way to make money? Today, no — and today I know it better

Not "we haven't found it yet". Today the space itself was **measured**, and
the measurement says how much there would be to find.

---

## Phase 1 — the database

Everything below runs on data gathered free, no paid API, nothing billed:
318 Binance perpetuals (hourly, up to 2 years), 178 Hyperliquid markets,
funding payments on both venues, 30 days of positioning data on 297 markets,
real order-book depth, and the Base chain read directly.

## Phase 2 — the analysis: four roads opened and closed today

| road | how it died |
|---|---|
| buying after a volume spike | looked good in sample, **zero on 173 untouched markets** |
| arbitrage between Binance and Hyperliquid | the gap is real (5.3% of hours beat the toll) but **closes inside the very hour you see it** — enter when you actually could, and gross is zero |
| the funding-rate difference between the two venues | **it works**: ~4%/year, no price risk, survives every check. But it is an interest rate: **€1 a year on €52** |
| short-selling newly listed coins | +6.30% in sample, **−1.87% on 365 unseen debuts** — one coin rose 345% in three days and ate every winner |

Plus, in the evening: positioning data (297 markets), ranking across markets
(318 markets), the same pair in several pools, and the last standing idea —
collecting a routing fee — which **dissolved**: those payments were not app
fees at all but token taxes (58 of 59 recipients collect on a single token).

## Phase 3 — the verdict, with a number

With **unlimited money**, the best road in the entire measured space would pay
about **€10 a day** — and only pretending the failed ones had worked.

The two walls are different, and that matters:

- **on-chain**: the wall is **capacity**. Slippage is 13% above $5,000. Finding
  an edge there changes little, because the ceiling stays at a few euros a day.
- **on liquid perpetuals**: the wall is **the signal**. €100,000 moves for
  0.043% — capacity is not the problem. An edge of even 0.1% would pay
  hundreds a day. We have nothing there because the edge is absent.

So the search belongs on liquid perpetuals: the hardest place to find an edge,
and the only one where finding it would matter.

## What was built today, which outlasts the roads

- a **calibrated yardstick**: a class-test difference of 2.2 is inside the
  noise — measured on a documented false positive. Every future test is read
  against it instead of costing a held-out sample.
- a **detector for my own archive edges**: if 3+ series share a start date, it
  is my downloader's floor, not an event. It caught two bad conclusions today.
- the rule that **two venues trading the same coins are one observation**, not
  a replication.
- the rule that a flow belongs to whoever it **co-varies with** — the test that
  dissolved the routing fee.

## The cash

**€52.16.** Untouched, as it has been throughout.

## What is yours to decide

`DECISIONE.md` had three options. The third fell today. Two remain.
