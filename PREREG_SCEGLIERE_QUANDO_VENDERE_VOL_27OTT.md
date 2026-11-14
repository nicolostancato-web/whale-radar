# Pre-registration — timing the volatility premium — 27 Oct, before the test

## The rule, fixed now

- Sell 30-day variance **only when the implied-volatility index is above its
  own historical median**, using only data available before entry.
- Non-overlapping 30-day windows.
- Return measured as (IV² − RV²) / (2·IV) scaled to 30 days.

## In sample (BTC + ETH, 98 windows, 4 years)

| | windows | return per window |
|---|---|---|
| IV above historical median | 44 | +0.549% ± 0.292 |
| IV below | 54 | +0.073% ± 0.292 |
| **difference** | | **+0.476% ± 0.413** |

A second split — IV rising versus 30 days ago — gives +0.482% ± 0.419.
Both barely clear their interval, and **five splits were tried**, so this is
exactly the situation that produced two false positives earlier today.

## The test, fixed before running

**SOL**, which is not in the sample the rule was found on. Deribit publishes
its volatility index.

**Pass requires both:**
1. the difference between the two halves is **positive**;
2. selling only above the median returns **more than selling always**.

**Fail:** either one. Then timing the premium is not demonstrated, and what
remains is the plain premium, which is an interest rate.

## Known weaknesses, stated in advance

- SOL moves with BTC and ETH. It is a **different asset, not an independent
  market** — a weaker held-out sample than I would like, and the best
  available.
- SOL's option market is younger, so fewer windows and less power.
- The median threshold was not chosen in advance.

---

# The held-out sample does not exist — same day

Deribit publishes a volatility index for **BTC and ETH only**. Of the 51
currencies it lists, the other 49 return nothing. The planned held-out asset
(SOL) cannot be used, and BTC+ETH are exactly the sample the rule was found
on.

So there is no out-of-sample test to run today, and saying so is better than
manufacturing a crooked one.

## Replaced by a forward test, which cannot be rewritten afterwards

`agents/prova_in_avanti_volatilita.py` opens a row per asset recording the
**prediction before the outcome exists**, and closes it 30 days later with
the realised volatility fetched then.

**First rows, opened 27 Oct 22:28 UTC:**

| asset | implied now | historical median | prediction |
|---|---|---|---|
| BTC | 37.7 | 50.4 | **stay out** |
| ETH | 53.2 | 64.2 | **stay out** |

Volatility is currently priced **below** its historical norm, so the rule says
this is not a moment to sell protection. That is a real, falsifiable call
recorded in advance: if the "stay out" windows end up paying as much as the
"sell" windows, the timing rule is dead.

Readable after **six closed windows — about three months.** No money is at
risk; this costs only time.
