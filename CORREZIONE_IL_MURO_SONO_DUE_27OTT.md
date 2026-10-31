# Correction: there are two walls, not one — 27 Oct, evening

Earlier today I published `IL_TETTO_DELLO_SPAZIO_27OTT.md`: a ceiling of
**€10/day with unlimited capital**, with capacity named as the binding
constraint everywhere. The verdict stands. **The reason was wrong**, and the
reason is what should steer the next move.

## The defect

The frontier's capacity figures were partly **invented by me** — €1,000 per
operation on perpetuals, €50 on a debut. Only one came from a measurement
(the on-chain slippage on Pons: 1.04% at $50, 13% above $5,000). Inventing a
constant instead of measuring it is the same error as the 0.30% fee that was
never read from the contract.

## The measurement

Real order-book depth, read from the public endpoint. **One-way slippage:**

| market | €52 | €10,000 | €100,000 | €1,000,000 |
|---|---|---|---|---|
| BTC | 0.0001% | 0.0001% | 0.0003% | **0.0054%** |
| ETH | 0.0002% | 0.0002% | 0.0002% | 0.0090% |
| SOL | 0.0050% | 0.0050% | 0.0060% | 0.0355% |
| **median of 10** | 0.0060% | 0.0102% | **0.0433%** | 0.1275% |

Capacity on liquid perpetuals was understated **by a factor of one hundred**.
A hundred thousand euros moves for 0.043% a leg.

## What this changes

The two walls are **different walls**, and collapsing them hid that:

| where | the wall |
|---|---|
| on-chain (memecoins, pools) | **capacity** — slippage is 13% above $5,000 |
| liquid perpetuals | **the signal** — capacity is enormous, the gross is zero |

On perpetuals, an edge of even **0.1% per operation** would pay hundreds of
euros a day, because €100,000 fits through each time. We have nothing there
because the edge is absent, not because we are too small.

## Consequence for the search

It reverses the priority. On-chain, finding an edge changes little: the
capacity ceiling caps it at a few euros a day no matter how good it is. On
perpetuals, finding even a small edge changes everything, because nothing caps
it until a hundred thousand euros.

**So the search belongs on liquid perpetuals** — the hardest place to find an
edge, and the only one where finding it would matter. That is an unwelcome
answer, and it is the one the measurement gives.
