# The first positive that survives its own interval — 23 Oct

Three months on the taker side produced eight negative verdicts. Grok's
correction — *the calibration row was showing you the money and you filed it as
a fuse* — moved us to the side that **collects** the toll. The first table from
that side is positive.

## Providing liquidity for a fixed, short time

All 5,023 graduated coins in the archive, no selection, common support across
every horizon. Entry at the end of minute one. Pool depth measured from price
impact (a ratio, so unit-safe). Our EUR 52 = 0.0157 ETH against a median depth
of 4.54 ETH → a 0.35% share. Price loss computed as √r − 1, stuck inventory at
−100%.

**Pools with a 1.00% fee**

| held for | net mean | net median | of which fees |
|---|---|---|---|
| **1 min** | **+0.8% ± 0.6** | +0.5% | +1.1% |
| **2 min** | **+1.5% ± 0.8** | +1.2% | +2.1% |
| 5 min | +0.4% ± 1.1 | −0.3% | +4.1% |
| 10 min | −1.3% ± 1.4 | −4.0% | +6.3% |
| 20 min | −5.3% ± 1.6 | −11.6% | +8.9% |

At 1 and 2 minutes the interval excludes zero. At 0.30% fee the same table is
+0.0% and +0.1% — indistinguishable from zero.

**Why the shape makes sense:** fees arrive immediately, the coin's collapse
arrives later. At two minutes you have collected 2.1% and the coin has barely
moved. At twenty you have 8.9% and the coin is down 14%.

## Validation that the measurement is right this time

Median pool depth came out **4.54 ETH**. The graduation threshold on this chain
is **4.2**. Two independent routes to the same number.

Two readings were discarded before this one, by our own rules: the first gave
+180% from price and 0% from fees (orientation inverted — `sqrtPrice` is tokens
per ether, so a collapse read as a gain), the second still had the scale wrong
(archive amounts are pre-scaled, `sqrtPrice` is raw).

## What must be removed before calling it profit

1. **Gas**: two transactions per position. Measured at 0.00001383 ETH each, so
   ~0.18% of our capital per round trip. Survives, but must be subtracted.
2. **The real fee distribution** of graduated pools. The whole result lives on
   the 1.00% tier; at 0.30% there is nothing.
3. **A pre-registered forward test.** This is still a measurement of the past.
4. Whether we can actually hold an in-range position for those two minutes
   against the 63 merchants already doing it.

---

## Correction, same evening: the +1.5% had look-ahead

The depth of each pool was estimated from the **whole** price series, including
swaps that happen **after** entry. Re-estimating depth from pre-entry swaps only,
and subtracting gas, the archive result is:

**+0.56% ± 0.83 over 5,110 coins — the interval contains zero.**

So the honest word is **not demonstrated**, not "+1.3% net". The headline figure
published earlier today was inflated by the look-ahead and is withdrawn.

### And the recent third is negative

| third of the archive | net | fees collected |
|---|---|---|
| oldest | +0.61% ± 1.58 | +2.28% |
| middle | +1.97% ± 1.50 | +2.50% |
| **most recent** | **−0.90% ± 1.21** | **+1.47%** |

Fees collected fell from 2.50% to 1.47%. This is the same thinning already
measured on this chain (10x outcomes from 18.2% to 7.9%, trades 848 → 382). The
merchant's trade thins with the market it serves.

Forward test 3 remains the arbiter, because it runs on **today**, which is the
only period that matters. It is expected to come out flat.
