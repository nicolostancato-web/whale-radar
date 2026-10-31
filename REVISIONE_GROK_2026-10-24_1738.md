# Revisione Grok — 2026-10-24 17:38 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 515s

---

I'll look up each fee address on public explorers and docs, and only name a product when a source actually ties the address to it.The first pass only labeled two of the eight. I'm checking Zora reward splits and LI.FI fee collectors against the remaining addresses.Zora’s reward events name the recipient role. I’m reading those logs, plus the LI.FI fee path, so the labels stay tied to a field in a transaction.The earlier pass named four of the eight recipients and left four without a public product. I am checking those load-bearing identities against public sources before writing the classification.Four of the eight addresses are Zora coin infrastructure or LI.FI’s protocol fee wallet. The other four have no public product name.

## 1. What each address is

| Address | Fees | What it is |
|---|---|---|
| `0x7bf90111ad7c22bec9e9dff8a01a44713cc1b1b6` | 36 | Zora protocol reward recipient. Base Blockscout: a Gnosis Safe proxy (`GnosisSafeL2`). Decoded `CreatorCoinRewards` and `CoinMarketRewardsV4` logs name this address as `protocol` / `protocolRewardRecipient`. |
| `0x0469a4bd3724dc86c9542f4694c976da13c450c0` | 19 | Zora’s Uniswap v4 hook. Uniswap hooklist: “Zora Hook” on Base. Base Blockscout verifies the contract as `ZoraV4CoinHook`. It receives the reward bundle from the Pool Manager and forwards the published splits. |
| `0xf1bc42fa0a54dab2b66a3bbd6b8e268d3d08d3af` | 10 | No public identity. Base Blockscout: a `CoinbaseSmartWallet` proxy, name `null`. The implementation is Coinbase’s smart-wallet contract. The account owner is not named. |
| `0x67421e82e0157a3ca9508ee92f6417a93bbf59cb` | 10 | No public identity. Base Blockscout: a Gnosis Safe proxy, name `null`. It receives Zora reward transfers beside the protocol Safe and the Doppler recipient. No product name is attached to the Safe. |
| `0xc8d077444625eb300a427a6dfb2b1dbf9b159040` | 7 | Zora hook, with a conflicting explorer label. Hooklist: “Zora Post Hook v2.3.0 (Base)”. Base Blockscout verifies the source as `ZoraV4CoinHook` and also marks the address `reputation: scam`. Etherscan labels it `Fake_Phishing4848764` / “Poisoning Address”; BscScan and Polygonscan use `Fake_Phishing4734884`. On Base it takes ZORA from the Pool Manager and pays the same reward recipients as the other Zora hook. |
| `0x5aafc1f252d544f744d17a4e734afd6efc47ede4` | 7 | No public identity. Base Blockscout: an EOA, name `null`, not marked a contract. |
| `0xc06ebbefd94032b85424d51906e2a335efae264b` | 4 | LI.FI protocol fee wallet. An EOA with no name tag. It is the caller of owner-only `batchWithdrawLifiFees` and the `_to` of `LiFiFeesWithdrawn` on Arbitrum, Moonbeam, and Fraxtal. Any LI.FI route can pay it. It is not Jumper’s own integrator wallet. |
| `0x885b00aa42f066d6c3fe944c10b1c6f8dbcdcd43` | 4 | No public identity. A second `CoinbaseSmartWallet` proxy, name `null`, same implementation as `0xf1bc42fa…`. Deployed through the same factory. Different account. |

No public product name: `0xf1bc42fa…`, `0x67421e82…`, `0x5aafc1f2…`, `0x885b00aa…`.

The other 26 of the 34 fee addresses in the sample were not looked up.

`0xf1bc42fa…` and `0x885b00aa…` are instances of Coinbase’s account contract. They are not Coinbase Wallet charging its interface fee. `0xc8d07744…` is labeled a poisoning address on several explorers; the hook registry and verified source are what identify the contract.

## 2. What the user came to do

Of the 97 fees on these eight addresses, 62 land on Zora’s own hook or protocol Safe (`0x7bf9…` 36, `0x0469…` 19, `0xc8d0…` 7). The person traded a Zora creator, content, or post coin. Zora’s hook takes the pool fee and pays it out. The user did not open a product called “the protocol Safe.”

Zora’s current split on creator and content coins, from [docs.zora.co](https://docs.zora.co/coins/contracts/rewards) and [support.zora.co](https://support.zora.co/en/articles/2509953) (August 2026), is a 1% pool fee: creator 0.50%, liquidity remint 0.20%, platform referral 0.20%, trade referral 0.04%, protocol 0.05%, Doppler 0.01%. Trend coins are 0.01%, all to the protocol. The platform referrer is fixed when the coin is created. The trade referrer is set per swap.

`0x67421e82…` is paid in those same splits and has no product name. The trade is still a Zora coin trade. Who invited the creator, or which app set the referral, is not published.

The four fees to `0xc06ebbef…` are someone using a route that pays LI.FI’s own service fee. The front end can be Jumper or any other LI.FI integrator. The receipt does not say which.

The two Coinbase smart-wallet accounts and `0x5aafc1f2…` have no published job. Nothing in public sources says wallet, terminal, Telegram bot, or aggregator.

## 3. Published size

Zora Coins, DefiLlama, read 24 October 2026. Two page loads the same day disagreed on the latest day and agreed on the history:

- Fees about $106 to $262 in the latest 24 hours, about $1.8k over 7 days, about $5.8k to $6.8k over 30 days. Cumulative fees $10.44m. Cumulative revenue $5.94m. October 2026 month-to-date fees $4,451.
- Monthly fees on that page: about $2.35m in July 2025, $2.51m in August 2025, $779k in September 2025, then $191k in January 2026, $11.6k in September 2026.
- MemeFees, fetched 24 October 2026 17:01 UTC from the same DefiLlama series: spot volume $4.1k for the latest day, $244k over 30 days, $79.41m over 365 days. Active wallets: not reported. A 1% fee on $4.1k of volume is about $41, and the reported day’s fees are $106, so those two columns do not reconcile. No volume is derived from the fees here.
- No Zora-published user count turned up.

Jumper, from Philipp Zentner’s post on 26 September 2026 and Jumper’s announcement carried on 28 September 2026: more than 100,000 monthly active users and more than $40 billion lifetime volume. That is Jumper across chains, lifetime. The address in this sample is LI.FI’s protocol wallet, which also collects from other integrators, and it appears 4 times in these 200 receipts. LI.FI’s own docs, 13 October 2026, state a 0.25% service fee, with volume discounts. That rate is not applied backward to turn fee totals into volume.

No user or volume figure is published for the Safe, the two smart-wallet accounts, or the EOA.

## 4. One-person products

None of the named entities is a known one-person or two-person app.

Zora’s hooks and the protocol Safe are protocol contracts. LI.FI was started in Berlin in 2021 by Philipp Zentner and Max Klenk and is a company; Jumper, incubated inside it, is being spun out under Marko Jurina as CEO. The September 2026 posts describe both as companies.

The four unnamed addresses are a Safe, two smart-wallet accounts, and an EOA. A Coinbase smart-wallet account can belong to one person. That is the account. There is no public product, and no public record of a solo or two-person team, behind any of them.

## 5. Where 0.204% sits

0.204% is the low end of interface and service fees that named products still publish, and it is the median of this sample.

It matches Zora’s platform-referral line, 0.20% of the trade. The lower quartile, 0.090%, matches Zora’s protocol slice plus trade-referral slice, 0.05% + 0.04%. In a decoded Zora payout, those two shares land on the protocol address when the trade referrer is that same address, which is 0.09% of the swap. The upper quartile, 0.755%, matches no published Zora line, and it was not tied to a named product.

Published charges next to it:

- Zora creator and content coins: 1% pool fee, of which 0.20% is the platform referral. [Zora rewards](https://docs.zora.co/coins/contracts/rewards), [Zora support](https://support.zora.co/en/articles/2509953).
- LI.FI: 0.25% service fee. [LI.FI docs](https://docs.li.fi/faqs/fees-monetization), 13 October 2026.
- Uniswap apps and API: interface fee set to zero. [@Uniswap, 28 December 2025](https://x.com/Uniswap/status/2005293403773583492). The change was part of the UNIfication vote (fee switch and a 100 million UNI burn).
- Rainbow: DefiLlama’s fee definition states 0.85% of trading volume.

No published measurement turned up of users leaving a named Base app because of a fee near 0.20%. Uniswap setting its interface fee to zero is a governance and product change, not a churn study.
