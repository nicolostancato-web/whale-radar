# Solana / pump.fun, measured end to end (22 Oct)

A reader was written from scratch for Solana — no logs to decode, instead the balance change of
whoever signed the transaction — and validated by the calibration before any result was read:
**-3.85% / -4.05% / -3.77%** on three independent tokens. Then the founder's whole list was
measured on 102 tokens with their **complete trade histories** (verified: none hits the 400
signature cap, so every series is a token's entire life).

## The lifecycle, which is the market the founder described

| lifespan | tokens | share | positions stuck | calibration | return |
|---|---|---|---|---|---|
| dies within 5 min | 41 | **48%** | **100%** | -5.36% | **-100%** |
| 5-30 min | 24 | 28% | 46% | -5.63% | -80.18% |
| 30 min - 3 h | 5 | 6% | 3% | -1.55% | -21.25% |
| **over 3 h** | 16 | **19%** | **2%** | -3.25% | **-7.05%** |

Half of pump.fun tokens die within five minutes and **every position in them is stuck**. The
survivors — the 19% where you can always exit — still return **-7.05%**, which is 3.8 points
*worse* than their own toll. So "catch the survivors" is not the answer: even holding only
them, and perfectly, loses.

## The early tell, which works and only tells you where not to go

| trades in first 60 seconds | tokens | stuck afterwards | return |
|---|---|---|---|
| fewer than 20 | 14 | 46% | -71.98% |
| 20-60 | 20 | **100%** | **-100%** |
| over 60 | 13 | **100%** | **-100%** |

A frenzied first minute predicts, almost perfectly, that nobody will be left to sell to. The
frenzy *is* the pump. A quiet start is a market that breathes — and still loses.

## Wallets: 4,347 addresses, 8,454 followable operations

- realised profit of the 171 genuinely active addresses: **median -60.6%, 13% in profit**
- grouped into **138 entities** (33 merges of addresses belonging to one operator — the same
  phenomenon found on the two previous chains)
- **copying them: median -100%.** Following a wallet means getting stuck.

## The best seat at the table, and it still loses

The first buyer of a token — on pump.fun almost always the launcher — returns a **median -50%**
with **16% in profit**, against **-100%** for every other buyer. Being first is genuinely worth
fifty points, and is still a losing median with one lottery winner (+62,687%) in 102.

And **27% of all selling comes from addresses that never bought the token** — in 24 of 102
tokens they are more than half the selling. Those who buy are largely buying from people who
were given their coins.

## One mechanism, all the rows

Across three chains and now the whole pump.fun lifecycle: **the apparent profit is the
inventory you cannot sell.** Measured directly, the relationship is monotone — tokens where
over half the positions are stuck show +18.80% if you count only those that closed, and -100%
when you count them all.

Cost of the whole Solana pass: **1,552 + ~12,000 Helius credits**, about 1.4% of the free
monthly allowance. Zero euros.
