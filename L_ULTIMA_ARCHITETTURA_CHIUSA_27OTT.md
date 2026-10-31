# The last open architecture closes — 27 Oct

Seven economic architectures were enumerated. Six closed with numbers. The
seventh — **the app that collects a routing fee** — stayed open because the
chain showed a large share of swaps paying a small cut to a third address.
This morning it was divided by seven (withdrawals had been counted as
transactions). This evening it closes entirely, for a different and deeper
reason: **those cuts are not app fees.**

## The test that settles it

An app fee belongs to **whoever routes**: the same app takes a cut across many
different tokens. A token tax belongs to **the token**: the same recipient
appears on swaps of that one token, no matter who trades it.

So: for each recipient, on how many distinct tokens does it collect?

| recipients collecting on | count |
|---|---|
| exactly 1 token | **58** |
| 4 tokens | 1 |

**98% are bound to a single token.** And one token alone pays **55 distinct
recipients** — that is a reflection token distributing to holders, not an
application.

A second, independent sign pointed the same way before the test: of 59
recipients, **zero** were paid in WETH or USDC. A real routing fee is taken in
good currency almost every time; a transfer tax is necessarily taken in the
token itself.

## What was actually being measured

Token transfer taxes and holder distributions — the token contract withholding
a share of its own transfers. That is not something you can **build**; it is
something you must **issue**. It is a different business with different
economics and a far worse reputation, and it was never the architecture under
consideration.

Exactly **one** address in the sample collects across several tokens, which is
what a genuine routing app looks like. One.

## Consequence

The third option in `DECISIONE.md` — build the fee-collecting product — rests
on a measurement that has now dissolved. It should not be chosen on the
strength of that number.

**All seven architectures are now closed with numbers.** That is not a defeat
to argue with; it is the map finally being complete, and it says the thing
being looked for is not in the space that was being searched.
