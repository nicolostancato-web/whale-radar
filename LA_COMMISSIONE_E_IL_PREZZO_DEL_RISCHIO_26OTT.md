# A fee is the price of a risk — 26 Oct

Following the newly named rut (*change why they pay you, not what you
predict*), the right category is **collect a contractual fee**. Providing
liquidity is exactly that — and it had failed twice for reasons **outside** the
category: memecoins killed it with price collapse, Base stables with a
near-zero fee.

So the combination worth hunting was: **stable pair + real fee + real volume**.
Searched across Base, Arbitrum and Polygon.

| chain | busiest stable pools | fee |
|---|---|---|
| Base | USDC/USDT, 1,122 swaps | **0.0004%** (measured earlier) |
| Arbitrum | none among the 40 busiest pools | — |
| Polygon | USDC/DAI, USDC/USDC | **0.010%** or unreadable |

Effectively zero everywhere.

## And the reason is not a market accident

> **A fee is the price of a risk.**

Liquidity on a memecoin pays 1% because you can be left holding a dead coin.
Liquidity between two dollars pays 0.001% because you risk nothing. Remove the
risk and the fee is competed to zero by everyone else who can also take no
risk.

So the thing I was looking for — **collecting a contractual fee without bearing
a risk** — does not exist by construction. It is not that we failed to find it;
if it existed, someone would already have bid it to zero.

This is the deepest form of the invariant so far, and it is worth more than the
ten closures before it, because it says **where not to look** rather than "this
one also failed".

## Why the surviving category survives

The app that collects a routing fee fits the same law and passes it: what you
bear there is **not market risk** — it is the work of building the thing and
bringing people to it. That does not get competed to zero, because it is not
free to replicate.

Which is also why it is the only candidate left after four independent routes
arrived at it.
