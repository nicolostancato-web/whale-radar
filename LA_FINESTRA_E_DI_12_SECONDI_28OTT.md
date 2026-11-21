# The window is twelve seconds — the fork test did its job — 28 Oct

Step 1 was: build it and replay a real liquidation on a local copy of the
chain, free, before any money moves. It took one evening and it killed the
plan — which is exactly what it was for.

## What the replay found

Forking mainnet at the block **before** each liquidation and reading the
position's health:

| case | premium | health one block earlier | window |
|---|---|---|---|
| A | **€79,010** | 1.0043 | **none — same block** |
| B | €1,276 | 1.0014 | **none — same block** |
| C | €186 | 0.9963 | one block |
| D | €148 | 1.0022 | **none — same block** |
| E | €90 | 0.9965 | one block |

And for the two that had a window, going further back: at **five blocks
earlier both were above 1**. So the window was **one block — twelve
seconds**.

**All five were taken within 12–24 seconds of becoming possible.**

## Why that excludes us, concretely

Our watcher reads health factors and discovers a position has crossed below
1 **at the end of the block where it happened**. The order goes out in the
next block. **We are always one block late** — and in that block the winner
has already taken it.

The winners are not watching health. They watch the **oracle price update
while it is still pending in the mempool**, know in advance which positions
will tip, and place their transaction in the same block. That is
mempool-level infrastructure plus bundle submission to block builders.

With the design I had — a watcher on public nodes — **we win nothing.**

## What this costs and what it bought

Cost: one evening, **zero euro**. It bought the knowledge that the plan as
designed does not work, before a wallet was created, before €20 was moved,
before weeks were spent building a watcher for a race already lost.

The earlier measurements were not wrong — no capital gate, no auction, deep
liquidity, an uncovered collateral niche. They were just not sufficient. The
binding constraint was never any of them: it is **twelve seconds**.

## What remains, honestly

One narrow possibility: Flashbots offers free bundle submission, and there
are free mempool streams. Whether a pending Chainlink update can be seen and
acted on with no paid infrastructure is a separate question — and a far
harder engineering problem than the one just invalidated.

Sample size: five. All five agree.

---

## A free channel does exist — and it is a different, harder road

Tested the same evening, before closing the file.

**MEV-Share**: Flashbots publishes a free, keyless stream of **hints about
private transactions**, precisely so that others can backrun them.
Measured: **~10 events/second**, and in four minutes of listening,
**17 carried the `AnswerUpdated` signature** (oracle price updates) and
**3 touched the Aave pool**. These appear **before** the transactions are in
a block.

Inspecting a hint: it carries the **transaction hash**, the `to` address,
and **log data** — which is what a backrun bundle needs.

So the route is:

1. a hint for an oracle update arrives, **ahead of the block**;
2. submit a bundle to Flashbots: *after that transaction, run my
   liquidation*;
3. if it is not profitable our contract reverts — and **a reverted bundle is
   not included, so it costs nothing, not even gas**.

That last property is unusual and worth stating plainly: **speculative
attempts are free.** We would not need to know in advance which position
tips; we could try, and wrong guesses would simply vanish.

## But this does not revive the previous plan

The simple design — a watcher reading health factors — **stays dead**. This
is a different and much harder build:

- react and sign a bundle in **under one block**;
- maintain a list of positions near the edge, which is **still the unsolved
  bottleneck** (the borrower list, blocked on Blockscout's rate limit);
- compete against actors already doing exactly this.

Honest status: **the road is not closed, but it is a harder road than the
one that was just invalidated**, and nothing about it has been measured yet
beyond the existence of the channel.
