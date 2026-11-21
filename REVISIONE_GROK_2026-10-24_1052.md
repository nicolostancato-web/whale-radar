# Revisione Grok — 2026-10-24 10:52 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 320s

---

I'll identify these Base routers from public sources and pull published integrator-fee figures, starting with the full addresses and their labels.Two of the eight are publicly named. The other six are not, and nothing in this sample is a small app collecting a published routing fee.

## 1. Names

| Address | What it is |
|---|---|
| `0x51C72848c68a965f66FA7a88855F9f7784502a7F` (16.1%) | **Wintermute**, market-maker inventory contract. Arkham entity label, Etherscan name tag, and the public Dune list of Wintermute addresses. Live since August 2023. Blockscout’s “MEV Bot” tag is a generic label and is the weaker one. |
| `0x6fF5693b99212Da76ad316178A184AB56D299b43` (2.8%) | **Uniswap Universal Router**, the current router in Uniswap’s Base deployment list. |

Not publicly identified, so not named:

- `0x83D55aCDC72027eD339d267EeBAf9A41e47490d5` (42.0%). No name tag. It holds about $1. In the swaps checked, the pool’s `recipient` was the Wintermute contract above and the call used selector `0x61fe21c0`. That is an observation, not an identity.
- `0x08FB33543aD633db94282df364AD80FEB8D9fc35` (7.2%). No name tag. Unverified. Holds on the order of $10M (WETH, USDC, cbBTC) and has millions of transactions.
- `0xd08b938153FfAa75fBE19339a56CC35CA11c0Fbc` (3.0%). No name tag. Deployed through the Gnosis Safe `CreateCall` factory `0xB22D635D552eC95142E2Abe3ffB859eA7d7C0316`. Near-zero balance, hundreds of thousands of transactions. Explorer shows `fulfillBasicOrder`; the bytecode contains the string “pool ids are only used for uniswapv4”.
- `0x278d858f05b94576C1E6f73285886876ff6eF8D2` (2.8%). No operator name. Optimism Blockscout titles the contract **StrategyExecutor**. Arkham has no entity. It holds on the order of $7M across chains.
- `0x4a8c4de8…` (2.5%, 3 swaps) and `0x9ee35bf1…` (2.4%, 209 swaps). No public name found.

The well-known aggregator routers are different addresses and are not these eight: 1inch `0x111111125421cA6dc452d289314280a0f8842A65`, Odos on Base `0x19cEeAd7105607Cd444F5ad10dd51356436095a1`, Kyber `0x6131B5fae19EA4f9D964eAc0408E4408b66337b5`, LI.FI Diamond `0x1231DEB6f5749EF6cE6943a275A1D3E7486F4EaE`.

## 2. Interface fee on the named ones

**Wintermute:** no published interface or integrator fee. It trades its own inventory.

**Uniswap Universal Router:** the contract does not charge one. Uniswap Labs’ own interface fee is **0% as of 27 December 2025**, on the interface and the wallet, separate from the governance protocol fee. Source: [What are Uniswap Labs’ fees?](https://support.uniswap.org/hc/en-us/articles/20131678274957-What-are-Uniswap-Labs-fees). The old figure was 0.25% on some pairs. The 0.15% assumption matches neither number. It does match what **0x** charges the user on its Standard plan, and that 0.15% is paid to 0x, not to the app.

## 3. How an app is paid, as published

The app’s rate is chosen by the app, inside a cap. There is no single published constant.

| Mechanism | What the app receives | Cap / their own cut | Newcomer |
|---|---|---|---|
| Calldata on Uniswap Universal Router or SwapRouter02 (`FeeOptions`: a percent of output and a recipient) | Whatever percent the transaction encodes | No protocol rate | Yes. Any caller, no account, no minimum volume. |
| [0x Swap API](https://docs.0x.org/evm/0x-swap-api/guides/monetize-your-app-using-swap) `swapFeeBps` + `swapFeeRecipient` | That many basis points of the sell amount | Default cap **1000 bps (10%)** per recipient. On the Standard plan 0x also charges **0.15%** on select pairs, and **keeps positive slippage**. | Account from the dashboard. Monetization is on the **$1,000/month** Standard plan ([pricing](https://0x.org/pricing)). Above 10%, or keeping the surplus, is a custom plan. |
| [1inch Classic Swap](https://business.1inch.com/portal/documentation/apis/swap/classic-swap/methods/v6.1/1/swap/method/get) `fee` + `referrer` | The `fee` percent, paid to `referrer` | **0% to 3%** | API key. The fee parameters are on the public swap endpoint. No volume minimum is stated. |
| [Odos](https://docs.odos.xyz/build/partner_code) `referralFee` + `referralFeeRecipient` | **80%** of the fee set; Odos keeps **20%**. Docs’ example is `0.001` = 0.1%. | No maximum is stated on the current partner page. | A referral code can be registered without a volume minimum. Free API tier is 1 request/second and 1,000 requests/day. |
| [LI.FI](https://docs.li.fi/guides/fees-monetization/faq) `integrator` + `fee` | The `fee` you set, paid to your wallet. Their FAQ still says LI.FI charges **0.25%** on top. The newer dynamic-pricing page says LI.FI’s own share is resolved per quote and the formula is not published. | Integrator fee plus extra recipients must total under 100% of the input. | Portal account. The SDK docs say the fee requires the integrator to be **verified**. |
| [Binance Web3 Trading API](https://web3.binance.com/en/dev-docs/products/trading-api/fee-and-revenue-sharing) `feePercent` + referrer | That percent, on Base | Greater than 0 and at most **5%** | Published as an API parameter. Whether key issuance needs approval is not stated on that page. |

## 4. Small and recent

The 223 addresses were not in the measurement output, so the other 215 cannot be dated from here.

Of the eight: Wintermute is a market maker trading its own book since 2023. The 42%, 7.2%, and 3.0% contracts are high-volume and unnamed, two of them with inventory or with flow settling to Wintermute. StrategyExecutor holds millions and is not a named fee app. Uniswap’s router is the retail interface and currently charges 0%. Three swaps at 2.5% of volume is a few large trades. No public source reviewed shows a small app earning a meaningful routing fee on Base. There is also no basis for calling the whole tail bots.

## 5. Volume for €500 in a day

Fee schedules price volume, not users. A user count needs an average trade size, which none of these schedules publish.

€500 divided by the app’s net rate:

| Net rate the app actually keeps | Routed volume per day |
|---|---|
| 5 bps (0.05%) | €1,000,000 |
| 10 bps (0.10%) | €500,000 |
| 25 bps (0.25%, Uniswap’s old interface rate) | €200,000 |
| 100 bps (1%) | €50,000 |
| 300 bps (3%, 1inch’s published maximum) | €16,667 |

At Uniswap Labs’ current interface fee of 0%, no volume produces €500. On Odos, a 0.10% referral fee nets the app 0.08%, so €500 needs about **€625,000/day**. On 0x, a 10 bps integrator fee is €500,000/day, with the $1,000/month plan on top, and the 0.15% still goes to 0x.
