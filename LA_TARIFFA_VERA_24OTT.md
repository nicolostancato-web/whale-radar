# The published rates, and two corrections to my own reading — 24 Oct

## Correction 1: those 223 "routers" are not an addressable market

- `0x51C72848…` (16.1%) is **Wintermute**, a market maker trading its own book
  since 2023.
- `0x83D55aCD…` (42.0%) is unnamed, holds about USD 1, and the swaps checked
  settle to **Wintermute's** contract.
- `0x6fF5693b…` (2.8%) is Uniswap's **Universal Router** — the retail interface.
- The rest are unnamed, several holding USD 7–10M of inventory.

So most of what I called a "contestable routing market" is **professional
inventory flow**, not users whose orders an app could carry. My reading of a
long contestable tail was wrong.

## Correction 2: the 0.15% I assumed does not exist

**Uniswap Labs' interface fee has been 0% since 27 December 2025** (it used to
be 0.25%). The 0.15% figure matches 0x's own charge to the user, which 0x keeps
— it is not what an app receives. My assumed constant matched nothing real,
which is the second time this week.

## What an app can actually charge today, published

| route | what the app keeps | gate |
|---|---|---|
| **Uniswap Universal Router `FeeOptions`** | **whatever percent the transaction encodes**, no protocol cap | **none** — any caller, no account, no minimum volume |
| 1inch Classic Swap `fee` + `referrer` | **0% to 3%** | an API key, no stated volume minimum |
| Odos `referralFee` | your rate, and you keep **80%** | a referral code, no minimum |
| 0x Swap API `swapFeeBps` | up to 10% | the **USD 1,000/month** Standard plan, and 0x still takes 0.15% |
| LI.FI | your fee, plus their 0.25% | portal account, integrator must be verified |

## The only number that matters

| if the app keeps | volume to route for EUR 500/day |
|---|---|
| 1% | **EUR 50,000/day** |
| 0.25% | EUR 200,000/day |
| 0.10% | EUR 500,000/day |

> **EUR 500/day = EUR 50,000 of daily volume through something of ours, at 1%.**

Not a share of Base. Not 962% a day. Not EUR 787,000 of capital. A product with
users who trade.

And the door is genuinely open: Uniswap's router honours a fee **encoded in the
transaction itself** — no account, no minimum, nobody's permission.

The remaining honesty: 1% is a high fee for a swap, so users need a reason that
is not price. At a realistic 0.25% the requirement is EUR 200,000 of daily
volume. That is a distribution problem, and it is the first one in three months
that is not blocked by capital or by latency.
