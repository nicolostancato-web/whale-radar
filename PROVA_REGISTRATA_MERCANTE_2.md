# Pre-registration 2 — the two-minute merchant, on graduated pools only

## Why test 1 was voided, after 13 positions and before any conclusion

Test 1 returned **+38% mean, 13 of 13 positive**, against an archive expectation
of +1.5%. A forward result twenty-five times better than its backtest is a
defect report, not a success, and thirteen wins out of thirteen is not a market.

Two causes, both named:

1. **The registered universe was not the measured population.** The archive
   figure (+1.5% ± 0.8) came from **graduated** pools. Test 1's universe was
   *every* pool with a 1.00% fee and no hook — which includes brand-new
   launches. The price component was +32% median: we were buying the launch
   ramp, which is the strategy already killed, wearing liquidity as a costume.
2. **No calibration row was computed in the live collector**, so the defect had
   to be caught by eye instead of by the instrument.

Data from test 1 is kept as `prova_mercante_ANNULLATA_1.jsonl` and is never
merged into any later result.

## The corrected rule

Everything from test 1, with three changes:

- **Universe**: pools that are **post-graduation** — the token must already have
  completed its Pons curve. A pool initialised with no prior curve history is
  excluded. Membership is decided from data available **before** entry.
- **Calibration row, computed every run**: positions whose pool saw **zero
  swaps** between entry and exit must come out at exactly **−gas**. Any other
  value voids the run.
- **Both-signs check, computed every run**: the price-only component must show
  **both signs**. If it is single-signed past 20 positions, the run is void.

Success, kill criteria and the 200-position target are unchanged from
`PROVA_REGISTRATA_MERCANTE.md`.

## The lesson, written where it will be reread

An archive result and a forward rule must name the **same population**, in the
same sentence. The population is part of the rule, not context for it. This
error was made two hours after writing the same lesson into memory.

---

## Test 2 also voided, after 12 positions

Same shape as test 1: **+31% mean, 11 of 12 price-positive**, against an archive
expectation of flat price at two minutes. The depth filter (≥3 ETH at minute
one) did **not** isolate graduated pools — new launches reach that depth too.

The error is the same one twice in two hours: **a universe defined by
resemblance instead of by the event**. "Full pool, no hook, 1% fee" describes a
graduated pool and also describes a launch.

The in-built guards did not catch it: there were no zero-swap cases, so the
calibration row never printed, and the both-signs check only arms at 20
positions. **Correct conclusion: the universe must be checked at the door, not
downstream.** A guard placed after the entry criterion cannot catch a wrong
entry criterion.

### Test 3 will use the event, not the resemblance

Admission requires the token to have **completed the Pons curve**, read from the
Pons contract's own graduation event. Not depth, not fee, not hook — the event.
