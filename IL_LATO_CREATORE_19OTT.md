# The other side of the table: what it costs to launch, what it collects (19 Oct)

Every strategy killed so far was a **buying** strategy, and all of them died the same way: the
information arrives after the price has already moved. The creator's side has the opposite
shape — nothing has to be predicted, and nobody has to be beaten to a block.

## The mechanics, measured not assumed

On 25 real launch transactions drawn at random from the native-quoted register:

- every launch attaches **exactly 0.0005 native (EUR 1.50)** of fixed fee — the five launches
  with no developer buy attach exactly that and nothing more
- anything above EUR 1.50 is an **optional developer buy** in the same transaction (7 of 12
  inspected had one, median EUR 27.74)
- gas: median **EUR 0.70**, worst seen EUR 4.36

So the floor cost of launching, with no developer buy at all, is **about EUR 2.20**.

## What a launch collects

Field [3] of every `CurveBuy` is the creator tax in native units. It is summed, not estimated
from an assumed percentage. On **500 native launches drawn at random** from the 424,571 in the
register (not from the coins that happened to trade):

| | |
|---|---|
| launches with no buy at all | 18% |
| launches with the tax set to zero | 31% |
| median collected | **EUR 0.01** |
| third quartile | EUR 3.31 |
| ninth decile | EUR 22.55 |
| **mean** | **EUR 24.49** (bootstrap interval **15.19 – 35.84**) |
| largest single launch | EUR 1,629 |

Removing the best launch leaves EUR 21.28; removing the ten best still leaves EUR 10.54. The
tail is wide but it is not one coin.

Against a fixed cost of EUR 2.20, the mean is **5 to 16 times the cost** — while **69% of
individual launches never earn their EUR 2.20 back**. This is a lottery with a positive
expected value, not a wage, and that distinction decides the sizing, not the decision.

## What is NOT yet proven

That the tax reaches the launcher. The chain has no archive node, so balances before and after
a taxed buy cannot be read. What is known: the curve stores the launcher in `deployer()`
(verified: it matches the transaction sender on 7 of 8 random launches, the eighth being a
launch through a contract), and `feeBps()` returns 100, i.e. the 1% curve fee in field [2] is a
separate thing from field [3].

**The only way to settle it costs EUR 2.20: launch one coin and watch where the tax goes.**
That is an outward action of a kind not taken before on this project — issuing a token that
other people can buy — so it waits for an explicit decision rather than being done inside the
loop.

## Scale, for context

- 424,571 native launches, by **301,329 distinct addresses**
- 90% of those addresses launched exactly once
- the 100 most active launchers account for only 7% of launches
- the busiest single address has launched **1,732** native coins

---

# Three checks the number had to survive

**Is the launcher taxing himself?** If the launcher buys his own coin, the 2% he pays comes
back to him and counting it as revenue inflates the figure. Separated by buyer address on the
same 500 launches: tax paid by **others** is EUR 24.41 of the EUR 24.49, tax paid by the
launcher to himself is **EUR 0.09**. Only **9%** of launchers buy their own coin at all. The
number survives untouched.

**Is it decaying, like everything else on this chain?** The buy side has been getting worse for
months (the 10x rate fell from 18.2% to 7.9%). The creator side moves the other way:

| third of the sample, by birth | mean collected | interval | launches not covering EUR 2.20 |
|---|---|---|---|
| oldest  | EUR 12.99 | 4.11 – 24.69 | 81% |
| middle  | EUR 19.99 | 7.17 – 37.31 | 70% |
| **most recent** | **EUR 40.05** | 19.20 – 66.88 | **58%** |
| last 50 of the sample | EUR 62.83 | 14.08 – 141.30 | 52% |

And the direction is understated rather than overstated: the youngest coins have had less chain
time inside the 2M-block window to collect anything.

**Is launching permissionless, or gated by their app?** Of 14 random launches, 11 go through
routers and 3 call the factory directly with selector `0xa72101af`. The call is fully readable:
name, symbol, an `ipfs://` metadata URI, a description, and **exactly EUR 1.50 attached, in
every single direct launch**. Two 32-byte words looked like they might be a server signature,
which would have gated the whole thing — checked across 10 direct launches: one of the two is
**constant**, so it is a configuration value, not a signature. Nothing suggests a permit is
needed.

**State: everything is measured except where the tax lands, and that costs EUR 2.20 to settle.**

---

# How far the free evidence goes on "who receives the tax"

The node offers no tracing at all (`debug_trace*`, `trace_*` all answer "method does not
exist") and keeps no archive state, so the internal transfer cannot be watched directly. What
storage shows instead:

- slot 0 of a curve holds the **token**
- slot 1 holds one address, the same one `deployer()` returns
- for the **20 highest-earning curves in the sample, slot 1 equals the launcher from the event
  in 14 cases**; in the other 6 it is a personal contract, not a shared router — no single
  address recurs more than once across the twenty

One of those six is suggestive rather than conclusive: the contract in slot 1 of the curve that
collected EUR 1,629 has made **exactly one transaction in its life** and holds **EUR 148.69**.
An address that never traded does not accumulate a balance by itself.

So the coherent reading is that slot 1 is the fee recipient, and that it is normally the
launcher. It is a reading, not a measurement, and the free routes to turn it into one are
exhausted. EUR 2.20 settles it.

---

# The call is built and already proved, for free

`agents/lancia.py` reconstructs the direct factory call from real launches rather than from an
ABI found somewhere — tuple of (name, symbol, uri, description, five empty social strings,
creator address, two zeros, a constant word, a per-launch salt), then two zero arguments and
empty bytes, with exactly 0.0005 native attached.

Encoding correctness does not have to be paid for: `eth_call` makes the factory run the code
and say whether it accepts. **It accepts**, and returns the address it would create. Then
`eth_estimateGas` prices our own transaction rather than someone else's:

| | |
|---|---|
| gas | 3,534,343 at 0.02 gwei = **EUR 0.21** |
| fixed fee | EUR 1.50 |
| **total to settle the question** | **EUR 1.71** |

The file refuses to send anything without `--vero`, and `--vero` is deliberately not wired up
yet. Nothing has been spent.

---

# How fast the money comes back

A lottery with a positive expectation is only playable if the stake comes back quickly enough
to be played again. On the 40 highest-earning curves in the sample, cumulative creator tax
(excluding anything the launcher paid himself):

| collected within | share of that coin's total tax |
|---|---|
| 1 minute | 30.3% |
| 10 minutes | 64.6% |
| 1 hour | 82.4% |
| 1 day | 94.7% |
| 1 week | 100% |

Two thirds of it lands inside ten minutes. Nothing is locked up: the EUR 1.71 is spent and the
outcome is known the same day, which is what makes repetition — and therefore the mean rather
than the median — the relevant number.

---

# The verdict: the EUR 1.71 launch earns EUR 0.55

Grok's review named the test that would settle it before any money moved: split the 500 by
what the **launcher chose at launch time** — fee only, or fee plus a developer buy, or fee plus
a list of snipe-tax-exempt wallets — and recount the tax with exempt addresses excluded on both
the `buyer` and the `recipient` side.

Two of my own mistakes had to be fixed first. The exemption event is
`SnipeTaxExempted(address)` with **one** argument; with two it matched nothing and reported a
confident "zero exempt wallets in 500 launches", which looked like an answer. And the exempt
count subtracted two addresses from a set that holds one whenever the launcher is the sender,
so the plain cell had collapsed to 3 launches instead of 121.

Corrected, with exempt wallets excluded from "others":

| cell | launches | tax from others | interval | from exempt | clear EUR 1.71 |
|---|---|---|---|---|---|
| all 500 | 500 | EUR 22.18 | 13.10 – 33.21 | 2.31 | 24% |
| **fee only, no dev buy, no exemptions** | **121** | **EUR 0.55** | **0.12 – 1.13** | 0.01 | **6%** |
| with exempt wallets | 123 | EUR 57.82 | 25.43 – 98.65 | 5.73 | 24% |
| with a dev buy, no exemptions | 255 | EUR 15.34 | 7.70 – 24.80 | 1.76 | 32% |

**The launch we were about to make is the first of those cells, and it earns EUR 0.55 against a
cost of EUR 1.71.** The whole confidence interval sits below the cost. Only 6% of such launches
ever cover their fee. Spending the EUR 1.71 would have bought one draw from a cell with a known
negative mean.

Note that Grok's precise mechanism — the creator taxing his own bundle — is not what inflated
the figure: tax from exempt addresses is only **9%** of the total. The real inflator is
**selection by the launcher's own stake**. Launches that put money in attract buyers; silent
launches do not. The EUR 24 was the average of people who paid to be noticed.

## And the cells that do collect are the buy side wearing a hat

The only way to collect is to put inventory at risk, and then the result is decided by the
inventory, not by the tax:

| assumption on the developer's own buy | net per launch |
|---|---|
| it all comes back (impossible) | +EUR 13.63 |
| it loses 6% (the round-trip cost) | +EUR 5.65 |
| it loses 20% | -EUR 12.98 |
| it loses half | -EUR 52.90 |
| it is a total loss | -EUR 119.44 |

Break-even sits at about an 11% loss on a median developer buy of EUR 60.60. And the tax cannot
be collected cheaply: launches with a dev buy under EUR 20 collect EUR 0.31 and EUR 1.55.

So the creator side is not a separate business. **It is a 2% rebate on the volume your own
stake attracts, and whether it pays is decided by the P&L of that stake** — which is exactly
the question six pre-registered buy tests have already answered in the negative.

**Closed. Nothing spent.**
