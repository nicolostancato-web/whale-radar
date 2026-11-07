# The gift channel is a farm, not an airdrop — 23 Oct

**Question (from Nicolo):** some wallets receive tokens they never bought and sell them.
How do they get them? Is that door open to us?

## What the chain says

Senders that deliver tokens to our profitable wallets:

| sender | total tx | distinct recipients (in 50 tx) |
|---|---|---|
| 3XDcE2tQ… | 1000+ | 14 |
| **4B8nfUUv…** | 1000+ | **28** |
| **B9uxeDGR…** | 1000+ | 23 (not yet tested) |

26 of the 28 recipients were served exactly **once** — the shape of an open
distribution, not an internal allocation. Recipients were a mix of brand-new
accounts (3-31 tx) and old ones (1000+). Twelve distinct funders across
fourteen accounts.

**All of that pointed to real people. It was wrong.**

## The tell the first reading missed

Eight recipients had transaction counts of 390, 393, 380, 379, 378, 379, 393, 381
— identical to within 1%. Pairwise overlap on the tokens they hold and the slots
they act in:

- **28 pairs out of 28** overlap
- four pairs at **Jaccard = 1.00** with 14-20 shared slots

Same tokens, same blocks, different addresses. **One operator, eight masks.**
The twelve distinct funders are not evidence of independence: funding each mask
from a different source is exactly what an operator does to look like a crowd.

`BegDtqRjVf3adLa7EMbL…` — one of the two wallets our clean ranking showed as
profitable on gifted tokens — is inside this fleet. Its ~53 SOL is one entity's
internal bookkeeping, and may be counted once per mask.

## Lesson for the instrument

Distinct funders prove nothing. The independence of addresses must be measured
on **co-activity** (shared tokens AND shared blocks), never on provenance of
funding, because provenance is the cheapest thing to fake.

Corollary already written into the code: near-identical activity counts across
addresses is a *detector*, not a coincidence.

## Still open

1. `B9uxeDGR…` has not been run through the co-activity test.
2. Whether distributions with **public criteria** exist (Grok, searching X).
