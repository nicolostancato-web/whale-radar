# Capacity, measured alongside the percentage — 23 Oct

New standing rule from tonight: **a 5% that holds EUR 200 is a percentage, not a
machine.** Capacity is measured on day one, not at the end.

For the merchant trade capacity has a closed form: fees = fee × volume ×
ours/(depth + ours), so the return per euro falls as 1/(depth + capital) and
halves when our capital equals the pool's depth. Median depth: **4.80 ETH ≈ EUR
14,500**.

| capital per position | net return | fees | euros per position |
|---|---|---|---|
| 52 | +0.57% ± 0.83 | +2.08% | +0.29 |
| 200 | +0.67% ± 0.83 | +2.06% | +1.33 |
| **1,000** | **+0.60% ± 0.83** | +1.96% | **+6.03** |
| 5,000 | +0.24% ± 0.82 | +1.59% | **+11.94** |
| 15,000 | −0.26% ± 0.82 | +1.09% | −39 |
| 50,000 | −0.82% ± 0.81 | +0.53% | −412 |

## Why this shape matters

The return is **flat from EUR 52 to EUR 1,000**. On the taker side, slippage
killed us at USD 5,000 and the usable size was ~EUR 200. Here usable size is
between **EUR 1,000 and 5,000** — the first candidate in three months whose
capacity could matter.

A position lasts two minutes, so **one stake serves all 46 graduations a day**.
At EUR 5,000 deployed: 46 × EUR 11.94 ≈ **EUR 550 a day**, from EUR 5,000 of
working capital.

## And the sentence without which the rest is noise

**Every interval contains zero.** The same data that says +0.24% also says
−0.58%, which is EUR 1,300 lost a day instead of EUR 550 earned. The recent
third of the archive is −0.90% ± 1.21.

**Status: the right shape, unknown sign.** The shape is rare and worth the wait;
the sign is decided by forward test 3, at 5 of 200 positions and accumulating
about two an hour.
