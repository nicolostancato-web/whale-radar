# The two positions that require no prediction, both closed (20 Oct)

Every strategy tried so far asked us to **predict**: where a coin goes, who is skilled, who
buys next. Two positions on this chain do not. Both were measured today, and both are closed.

## 1. Providing liquidity — structurally zero, closed in ten minutes

The idea: put money in the pool everyone trades against and collect a fee on every swap. No
prediction, no speed, no selection.

The pool's declared fee on every Pons graduate checked is **0.00%**. The ~1% paid on each swap
does not reach the liquidity provider: the **hook — the protocol — takes it**. A provider on
these pools earns nothing and carries the full loss when the coin falls, and these coins fall
(-37.8% one hour after a buy, measured on 5,094 coins).

This is structural, not statistical. No sample size changes it.

## 2. The graduation gap — real but smaller than the toll

When a coin graduates, liquidity moves from the bonding curve to a new pool. For an instant
there are two prices in two places. Capturing a gap requires only being there.

The first measurement said **+172% median**. It was false, and the verification gate caught it
before it was reported. Two defects:

- the curve price came from a file whose series does not reach the graduation block — on one
  case it was 24,000 blocks stale and worth a sixth of the true price
- the 80 coins measured were the ones that happened to sit in two of our files, out of 5,098:
  a sample of us, not of the market

Rebuilt with both sides read from the chain on **400 random graduates**, the median became
**+1.49%** — with a mean of +64.79%. Checking the extremes, as the rule requires, found a third
defect: the last curve buy was selected by block number **without breaking ties inside the
block**. When a coin graduates in a single block there are several buys in it, and the first one
is ~12x cheaper than the last, because the Pons curve rises 12.25x by construction. The giant
"gaps" were the curve itself, measured wrong.

With the tie-break fixed — **58 points of the mean were artefact**:

| period | coins | median gap | mean | above +6% |
|---|---|---|---|---|
| first half | 200 | +0.78% | +8.52% | 20% |
| second half | 200 | +0.37% | +3.93% | 10% |
| **all** | **400** | **+0.58%** | **+6.22%** | **15%** |

Against a round trip of about 6%: net mean **+0.22%**, **15%** of attempts in profit, **168 of
400 gaps negative**, and removing the ten best leaves **-4.21%**. The gap also halves between
the two halves of the period. Closed.

The residual tail is probably artefact too, of a subtler kind: a single buy that carries the
curve from its opening to graduation is recorded at the **average** price of that fill, not the
marginal price at the end — so the "gap" is mechanical.

## The structural map of this chain is now complete

| position | verdict |
|---|---|
| buying after a buy | -6.87% at our latency |
| copying skilled wallets | +3 points of real skill, -4% to -13% absolute |
| launching coins | EUR 0.55 collected against EUR 1.71 of cost |
| providing liquidity | **fee is zero: the protocol takes it** |
| graduation arbitrage | +0.58% median against a 6% toll |
| **the protocol itself** | takes ~1% of every swap — not accessible to us |

Three numbers died on the verification gate today, all for the same underlying reason: an
ordering or a join that picks the wrong case. Without the rule of checking one case on chain
before speaking, three discoveries would have been announced and built upon.

---

# 3. Arbitrage between two pools of the same token — closed

24% of graduated tokens live in more than one pool, and 21 of 25 second pools checked actually
trade. Both pools had to be native-quoted (comparing a native price with one quoted in another
token is the artefact that already inflated a number here by five orders of magnitude), and
prices had to be within 600 blocks of each other, because two distant prices differ because the
market moved, not because there is an arbitrage.

| period | comparisons | median absolute gap | above 12% |
|---|---|---|---|
| first half | 6,528 | 3.10% | 10% |
| second half | 6,529 | 3.01% | 9% |
| **all** | **13,057** on 109 tokens | **3.06%** | 10% |

Capturing a cross-pool gap costs two round trips, about 12%. The two pools stay within 3% of
each other. Closed.

---

# The map is complete, and the conclusion is structural

| position | verdict |
|---|---|
| buying after someone's buy | -6.87% at our latency |
| copying skilled wallets | real skill (+3 points), absolute -4% to -13% |
| launching coins | EUR 0.55 collected against EUR 1.71 of cost |
| providing liquidity | **pool fee is 0: the protocol takes it** |
| graduation arbitrage | +0.58% median against a 6% toll |
| arbitrage between two pools | 3.06% median against a 12% toll |
| the protocol itself | ~1% of every swap, not accessible to us |

Every position on this chain has now been measured, and they all fail in the same way: **the
toll is larger than the move available**. That is not a statistical result that more data could
overturn — it is arithmetic about the structure.

## The one pattern in the data that does make money, and why we are not building it

Launches that attach a developer buy and a list of snipe-tax-exempt wallets collect EUR 57.82
of creator tax on average, against EUR 0.55 for a silent launch. That is the pattern the
ecosystem's winners use, and 123 of 500 random launches do it.

Mechanically it is: issue a token, buy it through wallets exempted from the opening tax, and
let the resulting activity attract outside buyers who pay the tax. The money comes from those
buyers, and the activity that attracts them is manufactured by the issuer's own wallets.

That is wash trading. It is not a measurement problem or a capital problem — it is the thing
itself, and it is the reason the only profitable seat at this table is one we should not take.
