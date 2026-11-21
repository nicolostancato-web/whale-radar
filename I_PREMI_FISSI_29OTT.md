# Fixed bounties — probed and set aside — 29 Oct

The seventeenth family, chosen because it is the one shape that does **not**
pay capital: a fixed bounty to whoever performs an action. With Flashbots
bundles making failed attempts free, it fits the one new tool this search
produced.

## What the probe found

Four candidate contracts — Chainlink Automation registry, Gelato Ops, Aave's
rewards controller, MakerDAO's ETH-A clipper:

| | |
|---|---|
| contracts alive | **4 of 4** |
| logs emitted in 3.3 hours | **0** |
| windows failed | **0** |

Alive but **dormant**: these are superseded versions (Chainlink moved to
v2.3, Gelato to newer contracts, Maker became Sky). My addresses were old.

Worth noting the first version of this probe returned zeros with **five
failed windows per family** — the node refuses topic-only queries across all
addresses. Those zeros meant nothing, and the failure counter is the only
reason they were not read as "this family does not exist".

## Why I am not chasing the current addresses

The size is knowable without them. Comparable pots already measured in this
project: **Kleros jurors €21/day worldwide, UniswapX €40/day, Morpho
liquidations €94/day**. Fixed bounties are small by construction — they
reimburse gas plus a modest premium.

Even finding the live contracts, the family is **tens of euros a day split
among everyone**. That is below the threshold worth building for, and saying
so before spending the week is the point of having measured the comparable
pots earlier.

**Seventeen families. Cash €52.16, untouched.**
