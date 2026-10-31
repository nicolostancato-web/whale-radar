# Where we are — 24 Oct, morning

**Is there a way to make money? Not yet.** Fifteen roads measured and closed.

## The night and morning

| # | road | why it closed |
|---|---|---|
| 9 | filter out the merchant's tail | best filter on the first half is the worst on the second |
| 10 | overnight liquidity on tokenized equities | they are real (NVDA, SpaceX) but 1 pool of 917; the market is inside Robinhood's app |
| 11 | UniswapX fills | live and open, but EUR 40/day for the whole chain |
| 12 | the merchant, concentrated | −2.9% ± 0.4: concentration amplifies adverse selection |
| 13 | liquidation premiums | contractual (+2.6%, peaks +17%) — but at EUR 52 the whole of Base is **EUR 1/day** |
| 14 | the 0.30% stablecoin pool | **my own fallback**: the fee was 0.0004%, not 0.30%. Everything ÷750 |
| 15 | gap between two stable pools | 0.0009% median against a gas toll of 0.02–0.1% |

## The one sentence that fits all fifteen

**Every income on these chains is distributed either in proportion to capital,
or to speed — and where neither applies, the toll exceeds the gross.**

- toll > gross: whales, copying, both arbitrages, the 2x rule, the merchant, the stable gap
- pie too small: UniswapX (EUR 40/day), liquidations (EUR 94/day chain-wide)
- our capital: LP on Base yields 23%/year gross — EUR 12/year on EUR 52
- shut by construction: Jupiter Lock gifts, equities off-AMM

## What was built, which outlives the roads

- `agents/keccak.py` — event signatures **computed, not remembered**. It found
  Morpho at a non-canonical address; from memory it would have been "absent".
- `agents/dato_obbligatorio.py` — a missing value now **raises** instead of
  defaulting. Applied at 13 sites. Born from road 14, where an invented 0.30%
  survived four correct measurements and three hours.
- The instrument's rules, all enforced in code rather than remembered.

## Still open

One road: leveraged tokens (AAPLx3L, EUR 27M/day volume) — measurable only
while New York trades, 15:30–22:00 Italian time.

Cash unchanged at **EUR 52.16**. Nothing spent. No euro ever came close to
moving on a wrong number.
