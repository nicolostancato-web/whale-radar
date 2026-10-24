# Two figures that look contradictory and are not (19 Oct)

Running the outside guard net from the Mac surfaced a line that contradicts everything the
night established: on 1,984 recorded paths at threshold 1.5, "no stop, exit at graduation"
shows **+6% ± 3**, an interval that excludes zero. Against the frozen forward test's
**-6.77% ± 5.6** on 153 real positions, one of the two had to be wrong.

Neither is wrong. They are different populations.

The same state file, read as positions a strategy actually had to live through:

| strategy | closures | return |
|---|---|---|
| diploma-1.5 | 465 | **-22.77%** |
| diploma-3.6 | 112 | -17.39% |
| 50-5 | 437 | +11.52% |

And of those 465 diploma-1.5 positions, here is how they ended:

| ended by | count |
|---|---|
| stop | **372** |
| horizon | 49 |
| **actually graduated** | **44** |

So "exit at graduation" is a rule that fires on **9%** of the positions it is measured over.
Averaging the outcome over paths that reached a graduation prices a strategy by its survivors;
the 372 that were stopped out first are the strategy. This is the same family as every other
error this project has made with samples — the population was chosen by the outcome.

The honest numbers stay where they were: the frozen, pre-registered forward test at
**-6.77% ± 5.6**, and the live 50-5 at **-8% over 70 real operations**, against the same 50-5
showing +11.52% on paper. Paper and reality disagree by about twenty points, consistently, and
in the direction that flatters paper.

One thing worth keeping from the same run: the filter search reports `quota_venduta_prima`
(low) holding **+5.76%** on its unseen half — but on only 112 operations, which is thin enough
that it is a lead, not a result.

---

# The lead was noise

`quota_venduta_prima` (the share of trades that were sells before the 1.5 reserve crossing) was
reported at +5.76% on its unseen half, on 112 operations. Rebuilt on the full reserve series —
397 coins that actually cross 1.5 — with the threshold chosen **only on the first half** and
checked on the second:

| rule | selected | with the filter | without it |
|---|---|---|---|
| 50-5, first half (where I searched) | 99 | +4.91% ± 4.7 | +3.86% |
| 50-5, **unseen half** | 81 | **+8.93% ± 5.5** | **+8.75%** |
| hold 60 minutes, unseen half | 81 | -41.60% ± 16.3 | -41.34% |

The filter adds **0.18 points**. It is not a filter.

The same table says something louder about the 50-5 family: on simulated paths it earns +8.75%
without any filter at all, while holding the same entries for an hour loses 41%. The entire
apparent gain is the stop-and-target machinery acting on a simulated path — and live, over 70
real operations, that same rule returned **-8%**. Paper and reality differ by about twenty
points here too, in the same direction.

---

# Where the simulator lies: 5.24 points in one assumption

The paper-versus-reality gap has now appeared three times in the same direction. One assumption
accounts for a large part of it. Same 50-5 rule, same 397 coins, only the exit price changes:

| exit taken at | coins | return | ± |
|---|---|---|---|
| the price that triggered the rule | 397 | **+4.37%** | 3.0 |
| the next print | 397 | +2.63% | 3.6 |
| two prints later | 397 | +2.48% | 3.9 |
| **the first BUY print after the trigger** | 397 | **-0.87%** | 4.1 |
| five prints later | 397 | +2.83% | 4.6 |

A seller sells **to a buyer**. A sale does not execute against another sale, and the print that
trips a stop is very often somebody else's sale. Closing at the trigger price is therefore not
a small optimism: it is **5.24 points**, and it turns this rule from positive to negative.

The correction is written as a comment inside `_tocca` in `agents/prova_nella_curva.py`, in the
exact place that can repeat the mistake. From here, any rule evaluated on any chain gets its
exit table printed at trigger price / next print / first buy print — and **only the last one is
reported**.
