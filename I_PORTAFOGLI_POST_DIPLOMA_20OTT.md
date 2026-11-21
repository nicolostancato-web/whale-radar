# Post-graduation wallets: the skill is real, the size is not enough (20 Oct)

## What was measured

Every buy on the graduated Pons pools, followed **as we would live it**: entry 11 blocks after
theirs (our measured one second), target 2x, stop -50%, exit always on a sell print. Declared
before looking. The break-even against the real round-trip cost of about 6% is **37.3% of
followed buys doubling**; the market as a whole gives **29.36%**.

Wallets were grouped into **entities** first, because four of the five best addresses buy the
same coins in the same blocks — one operator with four wallets, not four skilled traders.
Counting addresses would have inflated the evidence fourfold. The grouping rule was declared in
advance: 80% symmetric overlap of coins *and* half the blocks identical.

## The result that matters: selection on period 1, checked on periods 2 and 3

| selectivity | entities | p2 doubles | edge | ± | p3 doubles | edge | ± |
|---|---|---|---|---|---|---|---|
| ≥40% | 4,120 | 34.1% | +3.70 | 0.66 | **29.5%** | +2.62 | 0.69 |
| ≥50% | 1,496 | 35.8% | +3.73 | 1.06 | **29.2%** | +3.07 | 1.14 |
| ≥60% | 404 | 36.7% | +4.80 | 1.79 | **28.2%** | +3.59 | 2.07 |
| ≥70% | 83 | 39.9% | +11.61 | 3.57 | **30.0%** | +7.20 | 4.18 |
| ≥80% | 18 | 52.1% | +17.60 | 7.65 | **18.0%** | +3.74 | 12.56 |

Two things are true at once, and both matter.

**The skill is real and it persists.** The edge over other buyers on the *same coins* is
positive in both unseen periods, at every selectivity, and the intervals exclude zero at the
broad thresholds where there are thousands of entities. This is the first persistent,
out-of-sample selection effect this project has found.

**It is not big enough to cash.** The bar is 37.3% doubles. In period 2 the selective cells
clear it (39.9%, 52.1%). In period 3 **nothing does** — the best is 30.0%. The market baseline
itself fell from ~30% to ~26% between the two periods, and a trader who is genuinely better
than average still loses money in a market that is worse than the cost of trading it.

## Why the spectacular numbers evaporated

One unseen period would have produced the headline "+20 points, we found something". The
+17.60 of period 2 becomes +3.74 in period 3, with an interval twelve points wide. The
difference is not the entities — it is the period. **Two unseen periods instead of one is what
separates a finding from a story**, and it cost nothing but the discipline to split three ways
instead of two.

## What stands as of this morning

- post-graduation universe rebuilt from the chain: **10,332 Pons graduates, 5,098 native-quoted**
  (our archive knew 847, i.e. 8%)
- swaps collected: **17.0 million** across 5,096 pools
- wallet ledger: ~13 million rows and still finishing, with 90% of trades carrying their native
  amount after the matching fix
- **entity-level selection effect: +2.6 to +3.6 points, replicated on two unseen periods**
- **absolute level in the most recent period: 30.0% doubles against a 37.3% break-even**

Not tradeable as it stands. The direction is established for the first time; what is missing is
either a cheaper round trip or an exit rule better suited to these entities — and that search
has to be run with the same three-way discipline, or it will produce another +20 that is not
there.

---

# The absolute return, which closes it

The edge table above measures how much **better than other buyers** the selected entities are.
It does not say whether following them makes money. Measured with the same rules, costs
included, selecting on period 1 and reading only periods 2 and 3:

| exit rule | break-even | period 1 (where chosen) | period 2 | period 3 |
|---|---|---|---|---|
| 2x / -50% | 37.3% | **+26.76%** ± 0.50 | **-5.69%** ± 0.60 | **-8.44%** ± 0.74 |
| 1.5x / -30% | 45.0% | +8.57% ± 0.22 | -4.12% ± 0.27 | -5.97% ± 0.33 |
| 3x / -50% | 22.4% | **+66.48%** ± 1.94 | -3.88% ± 2.19 | -10.77% ± 2.49 |
| 5x / -50% | **12.4%** | **+89.83%** ± 4.85 | **-13.03%** ± 5.20 | **-13.08%** ± 6.97 |
| 1.3x / -20% | 52.0% | +1.74% ± 0.12 | -4.20% ± 0.15 | -5.24% ± 0.18 |

All five rules were declared before looking, and the selection threshold was held fixed so that
only one dimension was searched. **Every one of them is strongly positive in the period where
the entities were chosen and negative in both unseen periods.** The 5x rule needs only 12.4% of
followed buys to succeed — one in eight — and still returns -13% twice.

**Both statements are true, and only together are they honest:**

- the selected entities **are** genuinely better than other buyers on the same coins, by +2.6 to
  +3.6 points, replicated on two unseen periods
- following them **loses money**, 4% to 11%, on those same two periods

Being better than a crowd that is losing is not profit. The market's own baseline fell from 30%
to 26% doubles while a round trip costs about 6%: there is no level of skill observable here
that bridges that.

The +66.48% in the period where the entities were chosen, against -10.77% in the next one, is
the most extreme case of retrospective selection this project has produced. Reading only that
column would have declared a money machine.

## Verdict

**Copying wallets post-graduation on this chain does not pay.** The phase closes with the
database built, the universe corrected from 847 to 10,332 graduates, and a transferable lesson:
relative edge and absolute return are different quantities, and every selection table from now
on carries both columns.
