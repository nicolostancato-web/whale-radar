# The real scale of the trade — 28 Oct, partial coverage

With four observations the liquidation trade looked like dust: median 59
cents, one occasion worth €617. **Blockscout's public archive** (free, no
key — the key I asked Nicolò for is no longer needed) gives real history.

## 31 valuable occasions

| | collateral seized | net premium at 5% |
|---|---|---|
| largest | **€735,254** | **+€36,762** |
| second | €145,995 | +€7,299 |
| third | €11,399 | +€569 |
| fourth | €9,758 | +€487 |
| **median** | | **€0.33** |

| threshold | occasions | share | sum |
|---|---|---|---|
| over €10 | 14 of 31 | 45% | €46,156 |
| over €100 | 7 of 31 | 23% | €45,819 |
| over €1,000 | **2 of 31** | 6% | **€44,061** |

Total positive net: **€46,159**.

## What this changes, and what it does not

**Changes:** this is not a dust trade. Occasions worth €7,000 and €36,000
exist. The earlier picture — "ten occasions a day, all pennies" — came from
four observations and was wrong about the scale.

**Does not change:** the shape is extreme. **One occasion is 80% of the
total.** With one such event observed, its frequency is unknowable, and the
mean is meaningless — the same lesson that killed the debut short.

## Coverage

8 of 88 windows succeeded (91% refused): roughly **11 days of the 60**. The
downloader now **records which windows it completed** and retries only the
missing ones, so each run adds real coverage instead of redoing the work —
the first version rescanned everything, including what had already
succeeded.

No number is quotable until coverage is most of the 60 days. What is already
safe to say: the occasions that matter are rare, large, and worth thousands.
