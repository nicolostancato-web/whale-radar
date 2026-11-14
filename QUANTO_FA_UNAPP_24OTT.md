# What an app actually earns on Base — 24 Oct

The six addresses seen collecting app fees, measured over three hours.

| app | received in valuable tokens | per day |
|---|---|---|
| `0x0469a4bd…` | EUR 26.94 / 3h | **EUR 216** |
| `0x7bf90111…` | EUR 2.70 | EUR 22 |
| `0xc8d07744…` | EUR 0.36 | EUR 3 |
| the other three | nothing valuable | — |

**These are lower bounds.** Only USDC, WETH and cbBTC were priced; thousands of
transfers in memecoins were skipped because an amount without its currency is
not a number. For apps that collect in memecoins the skipped part may be the
larger one.

## The order of magnitude, which is the point

**An app collecting swap fees on Base today makes between about EUR 20 and EUR
200 a day** in serious tokens. Not millions, not pennies.

Which puts the target in honest perspective:

> **EUR 500/day is between 2× and 25× the best of those six.**

Ambitious, but the same order of magnitude — unlike 962% a day, and unlike
UniswapX's EUR 40 a day for an entire chain. **First time in three months the
goal and a measured number sit on the same scale.**

## Two silent failures caught by the instrument, not by me

1. The RPC **rejects `null` as a topic wildcard** and answers nothing; the code
   read that nothing as "zero income" for all six apps. The correct wildcard is
   an empty list, and failures are now **counted and printed**.
2. A 3,000-block window is refused when the filter has no contract address —
   every window failed, and without the new failure counter that would have
   read as another clean zero.

Same family as the invented 0.30% fee: **a silent failure read as a datum.**
The counter is the enforcement.
