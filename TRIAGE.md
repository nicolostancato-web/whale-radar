# Triage — what to look at next, ordered by time-to-know

Nicolò's rule, 25 Oct: discard what is certainly impossible; among the rest,
**buy the cheapest information first**. Park the month-long ones until only
those remain.

"Time to know" = how long until I can say yes or no, **not** how long to build.

## Discarded — structurally impossible, no time spent

| candidate | why it is certain |
|---|---|
| Polymarket | **blocked in Italy** by ADM since July 2026. Not a strategy question, a legal one. |
| allowlisted RWA / tokenised funds | transfer restricted by construction; a stranger cannot hold them |
| Jupiter Lock style receipts | one named recipient per escrow, chosen by the creator. No way to enrol. |
| tokenised equities on AMMs | 1 trading pool of 917; the market is inside the brokerage |
| CoW solving, Jito bundles | whitelist or sub-millisecond auction; our latency is six orders out |
| monthly-rebalanced strategies, any kind | **arithmetically undecidable**: 865 cycles needed, ~120 exist |

## Open, ordered by time-to-know

| | candidate | time to know | why that long | what decides it |
|---|---|---|---|---|
| 1 | **new listings on Hyperliquid** | **2 hours** | the data is already downloaded; 178 first-candles | does price systematically do something in the hours after a perp lists? |
| 2 | **the attention candidate, on another venue** | **4 hours** | another public API, same code | do the 8/8 positive cells repeat where the search never looked? |
| 3 | **liquidation cascades** | **4 hours** | public endpoint, mechanical event, thousands of them | does price overshoot and revert after forced selling? |
| 4 | **HIP-4 outcome markets** | **1 day** | small venue, must map the contracts first | fee pool ~EUR 2,100/day — capacity may kill it before the signal |
| 5 | **UMA proposer / oracle disputes** | **1 day** | published rate (~$2/proposal), must count the daily proposals | is the pie more than a tip, and can a newcomer post the bond? |
| 6 | **Kleros juror** | **2 days** | rate published (EUR 10.46/coherent vote), draw probability is not | how often is a minimum stake actually drawn? |
| 7 | **Boros funding-rate markets** | **3 days** | ten days old, no published fee schedule, must be reverse-engineered | recency means thin; thin may mean reachable |
| 8 | **bridge relaying** | **1 week** | needs float on destination chains to even measure realistically | ~USD 10,000/day total, 3 addresses take 80% |
| 9 | **the fee-collecting app** | **weeks** | not a measurement — a product with users | EUR 169,000/day of routed volume for EUR 500 |

## Parked by the rule, not by judgement

Everything at 1 day or more waits. Items **1, 2 and 3** are today's work: they
cost between two and four hours each, the data is public, and each has a
mechanical reason to exist rather than a statistical hope.

If all three die, the next tier opens by itself.

---

## Update, night of 25 Oct: a screening threshold from the measured constants

Today's measurements give a number that screens candidates before any test:

| measured today | value |
|---|---|
| round-trip toll, taker, Binance/Hyperliquid perps | **0.09–0.10%** |
| maker advantage, measured not assumed | **+0.011%** per cycle |
| → **minimum gross any strategy must produce** | **~0.09% per cycle** |

Applied to what remains open:

| candidate | gross it would need | verdict on arithmetic alone |
|---|---|---|
| liquidation cascades | 0.09% per 4h cycle | plausible only if cascades are rare and large — **but then too few observations** (the same vice as new listings) |
| HIP-4 outcome markets | n/a | **dead on capacity**: EUR 2,100/day for the whole venue |
| UMA proposer | n/a — fixed fee per job | not a per-cycle strategy; survives the screen |
| Kleros juror | n/a — fixed fee per vote | survives the screen; the unknown is draw frequency |
| Boros funding markets | 0.09% per cycle | unknown, venue is ten days old |
| bridge relaying | 2–6 bps per transfer | **below the threshold by construction** unless we are the fastest, which we are not |
| the fee-collecting app | n/a — not a trade | survives: it has no toll |

**Three of seven die on arithmetic without a single test.** Two survive because
they are **paid work, not positions** (UMA, Kleros) — no toll applies to them.
One survives because it collects the toll rather than paying it.

That is the same conclusion arrived at from a third direction: on these venues
**the only things that are not killed by the toll are the ones that do not
pay it.**

---

## All three survivors resolved — the measurable phase is exhausted (26 Oct, 02:00)

| survivor | verdict | why |
|---|---|---|
| **Kleros juror** | **dead on capacity** | V2 on Arbitrum is live but tiny: **2 draws/day** for the whole protocol = ~EUR 21/day shared by every juror on earth |
| **UMA proposer** | **dead on capital** | the bond is **USD 750** against our EUR 52. Not a question of how many jobs exist — we cannot present ourselves, and one lost dispute wipes the entire capital |
| **the fee-collecting app** | **alive** | it is not a measurement. It is a product, and the decision belongs to Nicolò |

## The recurring number, now in four forms

| what pays | total, worldwide, per day |
|---|---|
| UniswapX solving on Base | EUR 40 |
| Morpho liquidations on Base | EUR 94 |
| **Kleros jurors, everywhere** | **EUR 21** |
| CoW solvers, all chains | ~EUR 13,000, half to one team |

Protocols holding hundreds of millions in value pay **tens of euros a day** to
the outsiders who work inside them. We are not losing to better competitors —
these markets are **vastly smaller than they look from outside**.

## The screening question, final form

Before asking *are we good enough*, ask **how much does it pay in total**. Under
EUR 100/day worldwide, no amount of skill matters.

## State

Everything decidable from data has been decided. What remains is either a new
candidate, a deepening of a type-B closure (see
`PROFONDITA_DELLE_CHIUSURE.md`), or the product path — which measurement cannot
resolve.
