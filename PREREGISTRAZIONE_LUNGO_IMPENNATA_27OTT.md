# Pre-registration — long after a volume spike — 27 Oct, before the test

Found only because the two-sided design was fixed: it could never see a
directional edge, and this one is directional.

## The rule, fixed now

- **Universe**: perpetual futures, hourly candles.
- **Signal**: the hour's volume is at or above the **95th percentile of that
  market's previous 500 hours**.
- **Direction**: **long**, unconditionally — the direction of the signal hour
  itself is ignored.
- **Exit**: **12 hours** later.
- **Observations**: non-overlapping.
- **Cost**: 2 legs. Binance 0.10%, Hyperliquid 0.09%.
- **Benchmark**: the same number of **long** entries at random times on the
  same market — this is what removes the market's drift.

## What has been measured so far

| | Binance large | Hyperliquid |
|---|---|---|
| rule, net of cost, 12h | **+0.0572% ± 0.0582** | +0.0097% ± 0.0657 |
| random long entries | −0.1580% | −0.0787% |
| **advantage over chance** | **+0.2153% ± 0.0747** ✓ | **+0.0884% ± 0.0876** ✓ |
| small markets (300-380) | +0.0636% ± 0.1493, not demonstrated | — |

**The relative advantage is demonstrated on two independent venues. The
absolute profit is not demonstrated anywhere.**

The gap is large because random entries lose heavily: crypto fell over the
period, so buying at random was a losing proposition, and the rule merely loses
less. *Losing less is not earning.*

## The test, fixed before running

1. **A third venue or a third period** the rule has never seen.
2. **Success requires the absolute net to be positive with its interval
   excluding zero** — not merely beating chance. A relative edge over a losing
   baseline does not pay rent.
3. The advantage over chance must also survive, otherwise the absolute result
   is just a rising market.

**Failure:** the absolute net is not demonstrated on the new data. Then this is
a relative effect only, and goes in the register as such — real, replicated,
and unprofitable.

## Known weakness, stated in advance

The 95th percentile and the 12-hour exit were **not chosen in advance** — they
come from earlier runs. This pre-registration fixes them; it does not undo the
fact that they were selected.

---

# OUTCOME — same day, test run as pre-registered

**FAILED.** 173 held-out markets, 37,454 operations.

| tier | absolute net | advantage over chance |
|---|---|---|
| f150 (62 markets) | −0.0627% ± 0.1159 | +0.0883% ± 0.1463 |
| f450 (67) | −0.1794% ± 0.1215 | −0.0285% ± 0.1514 |
| f600 (44) | −0.1593% ± 0.1386 | +0.0359% ± 0.1697 |

The absolute net fails the bar everywhere, as the in-sample numbers already
warned. But **the relative advantage fails too** — the part that looked solid.
Out of sample it is +0.09 / −0.03 / +0.04 with every interval containing zero.

## The real lesson, and it is new

The in-sample result looked strong because it "replicated on two venues":
Binance and Hyperliquid. **They are not two samples.** They trade the same
assets — Bitcoin, Ethereum, Solana. The same thirty coins, priced twice.
Agreement between them measures nothing except that the two exchanges quote
the same market.

A replication needs **different subjects**, not a different place where the
same subjects are recorded. The held-out tiers were different subjects, and
there the effect is absent.

## Still open, and honestly unresolvable with this data

The advantage was largest on the 30 biggest markets (+0.2153% ± 0.0747) and
absent from rank 150 downward. That could be a real size dependence rather
than luck. It cannot be separated here, because the biggest markets are
exactly the ones the rule was found on — there is no held-out sample of
large markets left to ask.
