# Revisione Grok — 2026-10-19 08:42 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 481s

---

The dataset will be wrong if trades, inventory, and copyable entries get collapsed into one row. I am checking how Pons graduation and Uniswap v4 actually settle so the missing fields are specific, not generic.The dataset, as specified, cannot answer the question you are actually asking. A `(wallet, coin)` aggregate with a first touch, a last touch, and two average prices cannot be turned back into "what do I get if I copy this buy one second later." That is the whole thesis, and it has to be stored as its own row or you will spend the week on a leaderboard you cannot trade.

Robinhood Chain is a single-sequencer Arbitrum Orbit chain with ~0.093s blocks, so one second is about eleven blocks. The Pons hook (`0xe5e702641ea86f4ae6cc3cdaed2b886f976be044`) has `afterSwapReturnsDelta`: the pool key says fee 0, and the hook skims the output via the delta. A sample of hook trades put that skim at a median of about 1%, with the creator's tax on top of it, both frozen at registration. The round trip is roughly twice that, before impact. Native-quoted pools settle the quote as ETH, which emits no `Transfer`.

## 1. The attribute you will regret

Store one row per attributed fill, not per position. The field the aggregate destroys is the pool's `sqrtPriceX96` and `liquidity` immediately after that fill, together with that fill's own token amount, native amount, block number, and transaction index.

That row is what makes the copy test computable: your fill is the first print at or after their block plus your measured latency, starting from the price after their impact, plus the hook fee, plus your own impact. Their first touch is often dust. Their average price mixes the early buy with a later chase. Neither one is a price you can send an order against.

Two fields have to sit next to that row or the fill table still lies.

- The token balance at the graduation block, as a quantity, with its bonding-curve cost in native. A boolean does not change a PnL number. The pre-graduation bag is what gets sold into the pool, and it will be booked as post-graduation profit.
- The hurdle for that coin, in basis points, read from the hook's registration: hook fee plus creator tax. Subtracting the fee field on the `Swap` event subtracts zero.

From the fill rows you can later compute, as of that block only, how many prior coins the wallet had and what copying them would have returned. An end-of-window win rate uses the future. It is not a repair you can run on the aggregate.

## 2. The join

Use the `Swap` log as the trade, and use the token `Transfer` only to name the person who ended up with the tokens.

Pull `Swap` logs from the PoolManager for those 847 pool ids. One stream, one contract. Each log gives you the transaction, the router (`sender`), the post-hook amounts, `sqrtPriceX96`, and `liquidity`. For a single-hop native pool, the native amount is the quote delta in that log. You never have to trace ETH.

Inner-join the memecoin `Transfer` logs on transaction hash. Net the token by address inside the transaction. An address that receives and forwards the same amount is a pipe. The trader is the address left with a nonzero net. Store three addresses in separate columns: that holder, `tx.from`, and `Swap.sender`. The router is not the trader.

Keep a transfer whose transaction contains no `Swap` for this pool in an inventory ledger. It changes who holds the bag and it has no price. A later sale of gifted tokens otherwise shows native out and zero native in.

Quarantine, and exclude from every ranking, any transaction where:

- the holder's net does not match the `Swap` memecoin amount
- the transaction contains another `Swap` (the native delta is then an intermediate hop, not what they paid)
- the holder is the hook, the locker `0x267444d099b10fb5ed7c3cc7b7c767adca574952`, the factory, the launch router, or whatever `feeEscrow()` and `buybackVault()` return on the factory

The hook later swaps accrued fees into quote. Those are real `Swap` events, and they are not a trader.

Before any PnL job, reconcile twenty single-hop buys by hand. The holder's token net should equal the `Swap` amount, and the gap between their execution price and the impact-adjusted spot should equal the registered hook-plus-creator fee. If either check fails, the attribution rule is wrong and the table stops there.

This is cheaper than the scan you have planned. The transfer scan is still worth running once, as the inventory ledger, but it is not where native size or price come from.

## 3. The false positive, and the guard

You will rank wallets on the realized multiple of round trips they have already finished, then credit the copy with their entry print.

The `-100%` rule does the selection for you. Anyone still holding is scored as a total loss, so the leaderboard is "who already sold." That multiple does not exist at the moment you would have had to follow them. Pricing your entry at their print is the same bug as last time: the pre-graduation simulator was optimistic by 5.24 points because it filled at the trigger instead of at the next print. Early post-graduation flow is also where a pre-graduation bag gets unloaded, and where any buyer looks good if the coin is about to trade. Burner wallets make it look like repetition. The first native funder misses the ones funded through a bridge or a centralised-exchange hot wallet, and it glues strangers together when the funder is shared infrastructure.

The guard is a one-page rule, written down and committed before any ranking query is run. It fixes all of the following, and a leaderboard computed without it is discarded:

- Ineligible: nonzero balance at the graduation block, funder linked to the creator, or a buy in the graduation block. Report that cohort on the side.
- Signal time is their fill's block. Copy price is `sqrtPriceX96` of the first swap at or after that block plus your measured latency, plus your size's impact, plus the hook and creator fee.
- The exit is declared now: their sell plus the same latency, or a fixed horizon. Open inventory is marked to the tape at that horizon.
- Wallets are chosen only on fills before time T. The number you report is computed only on fills after T.
- Ambiguous transactions are dropped, not imputed.

There is no column whose value is the price that triggered the rule.

## 4. The trap, and the day-one measurement

The trap is the same shape as last time, on a faster clock. Continuation after a buy lives in the next few blocks. Arrival-time ordering at one sequencer means a higher tip does not buy those blocks back, and the public sequencer feed lets faster senders see transactions before the block is even published. You cannot rebuild that feed from logs after the fact. What you can do is refuse to claim any move that happened before your order could land.

Day one is `Swap` logs only, for all 847 pools, with no wallet table. Nine coins is enough to estimate row counts and too few for a tail.

For every buy, start from `sqrtPriceX96` in that event, which is the price after they have already moved the pool. Measure the return to the first swap at or after +1 block, +11 blocks, +5 minutes, and +1 hour. Also measure, separately, the return from the price before their swap to the price after it, so you can see the number you would be stealing by filling at their print. Subtract that coin's round-trip hook-plus-creator fee.

Split by time since graduation (first 10 seconds, first minute, first 10 minutes, later) and by size quartile. And split the calendar at 29 September 2026, when the chain's gas subsidy ended.

Stop before building the wallet table if, in every stratum that has real volume, the size-weighted return from +11 blocks to +5 minutes does not clear that coin's round trip. Also stop if the first-minute stratum is the only one that clears it: that is a clock, and the wallet is a costume. The birth-time filters already came back flat once.

The same day, send a transaction and record wall-clock send time against the block it lands in. The horizon you test is that number, not the inherited one-second figure.

## 5. The week, in order

**First, the latency curve above, on all 847 pools.** Abandon the thesis if continuation past your measured latency does not clear fees, or if it clears fees only for people trading inside the same block as the leader. No attribution work is justified until this survives.

**Second, the frozen copy test on a chronological holdout.** Leaders are chosen by copy-PnL of their earlier fills, never by the realized multiple of the trade you are about to copy. Insiders stay ineligible. Open bags are marked to the tape. Abandon if the holdout mean, on the later period only, has an interval that covers zero or a mean below the fee hurdle. That is the same shape as the −6.77% ± 5.6 result that closed the last phase.

**Third, capacity, only on what survives the second test.** Drop each wallet's single best coin and recompute. Reprice the copy at one fixed size you would actually send, using impact observed on historical swaps of that size (`liquidity` is on the `Swap` log; early reserves are about 4.2 native, so a small order is a large fraction of the pool). Abandon if removing the best coin flips the sign, or if the size you can send consumes the edge. A wallet that made money in a size you cannot place is a closed question.

Build the fill table only after the first measurement survives, and build it for the holdout test, not as a 400,000-row scoreboard of realized multiples. The aggregate you have planned can be rolled up from the fills later. Rolled the other way, it cannot.
