# Technical capability: 100% — 31 Oct

```
position alive right now      health  1.0022
price drop of 3%              health  0.9722   (fallen)
flash loan                    10 WETH
liquidation                   executed
sale via aggregator           executed
loan repaid                   + fee

PROFIT ARRIVED IN CASSA:      0.392 WETH  ≈  $881
```

"Cassa" means **Nicolò's address**, `0x055e75…eB66`. Not mine, not the
operating wallet: the contract sent it there itself.

Everything in this test is real — the deployed contract, live aggregator
calldata, real Aave, real pools, current block. The only simulated element is
the price drop, which in reality arrives on its own.

## The three defects closed today

1. **Approving the wrong contract.** Aggregators do not pull tokens with the
   contract you call — they use a separate transfer proxy. Approving the
   wrong one gave `ERC20: transfer amount exceeds allowance`, which looked
   like bad calldata. The contract now distinguishes **who is called** from
   **who withdraws**.
2. **Amounts not aligned.** The quote carries a fixed amount; the liquidation
   seizes a slightly different one (the protocol keeps a share — 9.3969
   against 9.965 expected). The contract now writes the **real** amount into
   the calldata at the correct offset.
3. **Looking for the profit in the wrong place.** My test checked the
   caller's balance; the profit goes straight to the cassa. The system was
   right and the test was wrong.

## The full chain, verified

| | |
|---|---|
| see the price update before the block | ✅ 17 in 4 minutes |
| reaction window | ✅ **6.47s median** |
| compose the liquidation | ✅ **1.1s**, measured 129 times |
| Flashbots accepts the bundle | ✅ bundleHash issued |
| **complete liquidation, current block, live data** | ✅ **$881 to the cassa** |

## Why losing every race is unlikely

- **inside the block** — verified, with a receipt
- **time to spare** — 1.1s needed against 6.47s available
- **nobody is bidding** — €98,150 taken for €0.20 of gas
- **not a closed club** — 20 different winners across 24 large occasions
- **mistakes are free** — reverted bundles are never included

What remains unknown: whether the hint reaches them before us, and whether
they use direct builder relationships instead of this channel.

**Spent to date: 10 cents.** Cash €52.16 untouched, $38 of gas intact.
