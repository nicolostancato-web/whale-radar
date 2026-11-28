# Road 16: the toll side, measured from inside — 24 Oct

The reviewers named three doors where the discriminator is neither capital nor
speed. The first — **be the address the contract names** — is the only one that
compounds. Here it is in this chain's own numbers.

## The flow

Counting only pools born in the last ~8 hours (601 of them), and **ignoring 60%
of swaps** because they happen in older pools:

> **2,095 ETH an hour on the ether side = EUR 6.35M/hour = EUR 152M a day.**

What the toll side collects on that flow alone:

| who | per day |
|---|---|
| a venue taking 1.00% (a Pons-like contract) | **EUR 1,523,000** |
| an app that routes and takes 0.15% | **EUR 228,500** |
| an app taking 0.05% | EUR 76,000 |

This is the same structure that produced pump.fun's **USD 1.98M in one day**.

## The conversion that matters

> **EUR 500/day = routing about 0.2% of this chain's flow at a 0.15% fee.**

Not 962% a day. **Two tenths of one percent of market share.** It is the same
target, stated from the other side of the toll — and the distance between those
two sentences is what three months of measurement bought.

**But the currency that opens this door is users**, not capital and not speed.
That is a different problem, and measuring the chain does not solve it.

## Third instance of one error class, so it gets a name

Two earlier attempts at this measurement returned 10^38 ETH an hour. Cause, both
times and once last night with the leveraged token: **summing amounts without
knowing which currency they are in.** `amount0` is the first currency of the
pair, which is usually some token, not ether.

**An amount without its currency is not a number.** Before any sum, the unit
must be established per row — not assumed from the most common case.
