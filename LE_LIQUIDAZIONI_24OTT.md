# Road 13: liquidations — the first contractual profit, on a chain too small

Morpho Blue **is** deployed here (at a non-canonical address). Over 31 hours:
**13 liquidations, 10 a day, 7 distinct liquidators**, the busiest taking under
half.

The premium is written in the contract, not inferred from a pattern:

| loan | collateral | repaid | **premium** |
|---|---|---|---|
| USDG | USDe | 60.00 | **+2.62%** |
| WETH | WETH | 0.0010 | **+12.68%** |
| USDG | CASHCAT | 420.33 | **+10.19%** |
| USDG | PONS | 8.05 | **+17.12%** |

Median **+2.62%**, peaks above 17%. And the sizes **fit our capital exactly** —
repaying a 60 USDG debt is inside EUR 52.

## Capacity, applied before any enthusiasm

Across those 31 hours the entire chain produced roughly **EUR 55 of liquidation
premium**, split among seven liquidators. Taking literally all of it would be
**EUR 40 a day**, and winning it means being faster than seven bots.

**On this chain it is a tip. But this time the mechanism is not the problem —
the venue is.** Morpho's liquidation incentive is written into the same
contracts everywhere, and on Base or Ethereum the protocol carries hundreds of
millions rather than fifty-five euros.

**First time in three months that the sentence is "the strategy is not wrong,
the chain is too small."**

## Built tonight and reusable

`agents/keccak.py` — keccak256 in pure Python, so event signatures are
**computed rather than remembered**. Verified against two known topics.
Trusting memory for a signature is the same error as trusting a code comment
for a price: it ages without warning. It immediately found Morpho at an address
that is not the canonical one.

---

## And on Base, where the market is large: closed too

Four days, Morpho Blue on Base, 71 liquidations (~10/day), 19 liquidators, the
top two taking half.

| capital available | pie for the **entire market** |
|---|---|
| EUR 52 | **EUR 1/day** |
| EUR 300 | EUR 5/day |
| EUR 1,000 | EUR 8/day |
| EUR 10,000 | EUR 54/day |
| unlimited | **EUR 94/day** |

The profit scales almost linearly with capital. At our size the whole of Base's
liquidation market is **one euro a day**, split nineteen ways. Even with
unlimited capital the entire market is EUR 94 a day.

**Closed on both chains — and for a reason worth remembering: this is not a
skill problem. The trade pays in proportion to the money you put in, and we do
not have it.** The mirror image of the merchant, where capacity was the limit;
here the limit is us.

## Night tally

Five roads closed: the tail filter, tokenized equities, UniswapX, the merchant
in full, and liquidations on two chains. One remains — leveraged tokens,
measurable only while New York is open.

One tool built that will outlast all of them: `agents/keccak.py`. It is why
Morpho was found at a **non-canonical address**; from memory it would have been
recorded as absent and the road closed for the wrong reason.
