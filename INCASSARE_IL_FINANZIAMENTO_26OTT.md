# A different architecture: be paid to supply the missing side — 26 Oct

Following the law (*income pays whoever bears something*), this is not a
prediction. Short the perp, long the spot: **delta-neutral**, indifferent to
price, collecting the funding that longs pay shorts every hour. What you bear
is capital tied across two legs, basis risk, and the risk that funding flips.

175 Hyperliquid markets, **1,384,872 hourly funding readings**.

## The result reverses the trade

| horizon | gross funding collected | after entry cost (4 legs, 0.18%) |
|---|---|---|
| 24h | **−0.0306% ± 0.0026** | −0.2106% |
| 7 days | **−0.2145% ± 0.0333** | −0.3945% |
| 30 days | **−0.9232% ± 0.2093** | −1.1032% |

Funding is **net negative** on this venue over this period: **shorts pay
longs**, not the other way round. So the paying trade is the mirror — long the
perp, short the spot.

## And that is exactly the side we cannot take

Shorting spot requires borrowing the asset, and the borrow costs — often more
than the funding it would collect. The side we **can** do without borrowing
(short perp, long spot) is precisely the one that **pays negative**.

> **Of the two directions, the accessible one loses and the paying one is not
> accessible.**

## Why it was still the right thing to test

It was a genuinely different economic architecture — being paid for supplying a
side rather than for forecasting — and the first such test. The answer is that
on this venue someone already supplies that side, and the payment goes to
whoever does the opposite of what we could do.

That is a structural block, not a measurement one, and it is now known.
