# One evening on FX and commodities — 25 Oct

## What was built

A **generic** data machine: any symbol, free sources, declared counts. Acquired:
EUR/USD and six commodities (copper, oil, gold, gas, silver, wheat) — ~17,300
hourly candles each over two years, plus 10-year daily series.

## EUR/USD hourly: closed

Six classic rules × three horizons, threshold chosen on the first half and
checked on the second, never seen.

**The calibration row works**: random entries return −0.0515%, −0.0421%,
−0.0377% against a declared toll of 0.05%. The instrument reads correctly.

Every rule lands between −0.03% and −0.07% — **the toll and nothing else**. The
one that looked positive on the first half (+0.068%) is −0.027% on the second.

What makes this stronger than the memecoin results: there the toll was 6% and
hid everything. **Here the toll is 0.05%, so even a tiny edge would show.** It
does not.

## Commodities: a trap caught, then a candidate that did not confirm

The first sweep showed many positives — including **four opposite rules all
winning on silver at 72h**. Opposite rules cannot both be right: that was the
market rising, and every rule buys and holds, so they inherit the tide.
Corrected by benchmarking each rule against **random entries on the same market
and horizon**.

With that correction, 13 of 126 rules beat chance (≈3 expected). Two showed
**internal coherence** — variants of one idea agreeing rather than contradicting:
gold breakouts, copper breakdowns.

But the scan **burned the holdout**, so those were candidates, not findings.
Pre-registered them (`PREREGISTRAZIONE_ORO_RAME_25OTT.md`) and tested on the
10-year **daily** series, never used:

| | difference from chance | verdict |
|---|---|---|
| gold breakout, 6 | −0.113% ± 0.399 | not demonstrated |
| gold breakout, 24 | +0.475% ± 0.721 | not demonstrated |
| copper breakdown, 6 | +0.696% ± 0.788 | not demonstrated |
| copper breakdown, 24 | +0.785% ± 1.088 | not demonstrated |
| copper breakdown, 72 | +0.393% ± 2.232 | not demonstrated |

By the rule written before looking, the candidates are dead as findings.

**Flagged for what it is:** 4 of 5 carry the same sign as the hourly result.
Four heads in five happens one time in five by chance, so it is not evidence —
but it is not five scattered signs either. The intervals are wide because the
samples are small (n=109 copper, n=201 gold).

**Honest reading: not demonstrated, with a weak hint not yet extinguished.**
What would settle it is not a new idea but **more data** — the same rule across
more metals and more years. Hours of work, not a month.

---

## Both candidates dead, same evening

**Gold breakout — dead.** Applied unchanged to 19 markets: only 5/19 and 10/19
positive, mean **negative** (−0.351%, −0.259%). Gold was one lucky market among
many, not a rule.

**Copper breakdown — dead.** It generalised better (14/19 and 13/19 markets
positive, mean +0.20% and +0.40%) but split by time it collapses:

| horizon | first half of the history | second half |
|---|---|---|
| 6 | **−0.085%** | +0.459% |
| 24 | **−0.066%** | +1.009% |

11 of 18 positive in the first half — a coin flip — and 13 of 18 in the second.
**A rule that works only in one period is not a property of the market; it is
something that happened.**

A caveat stated before the count was believed: commodities move together — oil,
gasoline and heating oil are nearly one market — so 19 markets are not 19
independent tests, and the "14 of 19" was optimistic from the start. The
time-split check does not depend on that correlation, which is why it was the
right one to run.

## What the evening actually bought

Not a method. **Speed.**

Three months to the first verdict on crypto. **One evening** to: build a generic
data machine, acquire 19 markets, calibrate the instrument (random entries
return exactly −toll), close EUR/USD, catch the tide trap on silver, promote two
candidates, pre-register them, and kill both.

The number worth tracking is not the result but the time to recognise that a
thing does not work. It fell by about a hundredfold.
