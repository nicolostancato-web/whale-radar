# Revisione Grok — 2026-10-25 09:25 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 467s

---

I'll map permissionless on-chain markets and paid functions with published volumes and fee pools, and mark each against the four killers. First I'm pulling current venue data and any notes already in this workspace so the figures stay sourced.Nothing on this list clears €10/day for a €52 account with a one-second laptop and no inventory. The single closest item is a Kleros juror vote: one coherent vote on the General Court pays about €10.46, the minimum stake is about €17, and the judgment is a multi-day vote. I could not find how often a minimum-stake juror is drawn, so that is a per-vote figure, not a daily income.

Euros below use €1 = $1.1203 (Cinco Días, 25 Oct 2026, 07:40 UTC). Figures are venue totals, not a share a €52 account can take. A fee pool is money traders pay. It is income only where a protocol pays an outside party.

## 1. What is actually tradeable beyond spot tokens

**Perpetual order books, crypto underlyings.** DefiLlama’s perp page, 25 Oct 2026, shows $13.25 billion of perp volume in 24 hours and $13.40 billion of open interest. Hyperliquid is $5.17 billion of that volume and $7.57 billion of open interest. OpenChainBench (25 Oct 2026, 07:24 UTC) puts Hyperliquid’s fees at $78.14 million over 30 days, about €2.33 million a day, with a measured all-in cost of 4.7 bps on 10x ETH. Lighter’s normalized 24-hour volume is $1.43 billion (DefiLlama). Its 30-day fees are $3.59 million on one OpenChainBench page and $5.87 million on another, so about €107,000 to €175,000 a day, at an all-in of 0.2 bps. Base-tier Hyperliquid makers pay 1.5 bps. They do not receive it. Killer for this profile: toll, capital, and latency. The book is already occupied by makers who live under a millisecond.

**Perps on stocks, commodities, indices, FX, and pre-IPO names.** These are synthetic contracts margined in USDC, not the tokenized shares already measured. trade.xyz, the dominant HIP-3 deployer on Hyperliquid, shows $6.74 million of fees and a very large open interest on its DefiLlama protocol page (30-day fees $6.74 million; a second DefiLlama table shows $6.51 million). That is about €200,000 a day of fees. Cipher Intelligence, 25 Oct 2026 06:41 UTC, counted 164 live HIP-3 markets and $484 million traded that morning, $457 million of it on trade.xyz: 98 stock markets, 9 commodities, 4 indices, 3 FX, 2 pre-IPO. Growth-mode taker fee is 0.9 bps and the maker still pays 0.3 bps (trade.xyz docs and Hyperliquid docs). Deploying a market requires staking 500,000 HYPE. Trading does not. I could not find today’s volume split between FX and commodities. Killer: toll plus capital plus latency. The fee pool is large and it is paid by the trader.

**Ostium, the specialist FX and commodity book on Arbitrum.** DefiLlama’s protocol page: 24-hour volume $852,182, 24-hour fees $751, 30-day volume $125.67 million, 30-day fees $132,347. The 30-day fee average is about €3,900 a day. The same site’s exchange page shows $1.42 million of volume for the day, so the daily print is noisy. Opening fees are 1–10 bps by asset class, plus a $0.10 oracle fee (Ostium docs, 8 Oct 2026). On the RWA perp page, EUR-USD had $11.61 million of volume and an estimated $5,804 of fees over 30 days. Gold had $5.15 million and $2,574. Killer: pie too small, and quoting it still needs margin.

**Ondo’s stock and index perps.** DefiLlama’s perp table lists Ondo at $47.05 million reported volume and $105.74 million of open interest in 24 hours, and $5.43 billion over 30 days. One contract page, US500, snapshotted 15 Oct 2026, had $26.18 million of volume that day, maker fee 1.01 bps, taker 2.51 bps. The access-model field on that page was blank. I could not confirm the book is usable without an Ondo account. Ondo Global Markets’ tokenized stocks, a different product, did $25 million of DEX volume in 24 hours (DefiLlama), and primary RWA issuance of this kind is allowlisted. Killer: closed by construction where the token itself is allowlisted. The perp, if it is a plain USDC-margined book, falls back to toll, capital, and latency.

**Options.** DefiLlama’s options page, 25 Oct 2026: notional volume $60.46 million, premium $1.52 million, fees $12,954 for the whole category. About €11,600 a day. Derive is $49.54 million notional and $9,104 of fees. Aevo premium is $12,298. Panoptic’s own fee page shows about $35 that day and $3,048 for October to date. Rysk’s premium that day is $78,710. Its fees are blank on the rankings, so I am not inventing them. Killer: pie too small, and an options book needs inventory.

**Yield tokens and funding-rate tokens.** Pendle V2’s fees averaged $15,890 a day over seven days (InsideBitcoins, 25 Oct 2026), about €14,200, on $1.06 billion locked. That is an AMM. The toll problem already measured on spot AMMs applies. Boros, Pendle’s funding-rate market, did $22.8 million of perp volume in 24 hours and $150.75 million in seven days (DefiLlama). A secondary post citing Pendle’s investor dashboard puts Boros open interest near $130 million and annualized revenue near $800,000. I did not open that dashboard, and I did not find a published fee schedule. The spread markets added on 15 Oct 2026 reference Gate as well as Hyperliquid, and Gate is a KYC exchange. Killer: requires capital. The CEX leg is closed by construction.

**Prediction markets.** Polymarket’s DefiLlama page, 25 Oct 2026: fees $5.16 million in 24 hours, of which $3.43 million is off-chain (Polymarket US, a CFTC venue) and $1.72 million is Polygon. Polygon price-volume was $131.25 million, notional $262.37 million. Polygon revenue was $1.19 million, so about $530,000, roughly €473,000, is the combined day of maker rebates, taker rebates, referrals, liquidity rewards, and holding rewards. I could not find a published split of that €473,000. Italy is on Polymarket’s own blocked list, ADM blacklisted the site on 10 July 2026, and access has been cut at Italian providers since 27 July 2026. Killer for a person in Italy: closed by construction. Polymarket US is KYC. Kalshi is not on-chain and not permissionless.

HIP-4 outcome markets on Hyperliquid went live in May 2026. DefiLlama: fees $71,144 over 30 days, about €2,100 a day. Fees are charged on close, and there is no maker rebate. Hypersight shows $296 million traded over the life of the archive. I could not confirm a clean 24-hour volume from that page. Killer: pie too small.

The long tail (Opinion, Predict.fun, Limitless, Azuro, Overtime, SX Bet) I only have from a Dune dashboard last updated 27 July 2026. That is three months stale. I am not using it as today’s size. Limitless was already down to tens of thousands a day in that snapshot.

**RWA balances that are not markets.** DefiLlama’s RWA dashboard, 25 Oct 2026: $30.76 billion active AUM, $4.33 billion actually sitting in DeFi, RWA-perp open interest $19.36 billion, RWA-perp volume $6.77 billion in 24 hours. The volume is mostly the perp books above. Securitize, Franklin, Circle, and BlackRock-style funds are allowlisted. Centrifuge’s estimated annual revenue of $2.37 million is an issuer-disclosed management fee, not a spread a stranger quotes. Killer: closed by construction.

**Compute, storage, domains, items.** Akash, Render, io.net, Filecoin, and Livepeer pay operators for useful work, and the work requires GPUs, disks, or a hotspot. That is inventory, which this profile does not have. I did not find a current published daily euro payout for laptop-bandwidth networks (Grass and similar), nor a current OpenSea, Blur, or ENS secondary volume. I am not filling those in.

## 2. What appeared in the last year and is still thin

HIP-3 launched 13 Oct 2025, twelve days outside a strict twelve-month window. It is not thin. trade.xyz alone is a ~€200,000-a-day fee pool.

Inside the window, and still small:

* HIP-4 outcome markets, May 2026, outside deployers from 29 Aug 2026. Fee pool about €2,100 a day.
* Boros funding-rate markets, already $22.8 million a day, with spread markets ten days old. The fee total is not in a primary source I could open.
* Panoptic’s fee line only became non-zero in mid-2026, and the whole protocol collects about €30 a day.
* The 2025–26 perp venues behind Hyperliquid (Lighter, Aster, edgeX, GRVT, Pacifica, Extended, Nado) already print hundreds of millions to billions a day. Recency did not leave them empty.

Variational reports $761 million of 24-hour perp volume on DefiLlama with the normalized-volume cell blank. I am not treating that as confirmed, and I did not find its access rules.

## 3. Where a protocol pays an outsider for being right

| Function | Payer | Published rate | Paid out per day | What I could not find |
|---|---|---|---|---|
| Polymarket liquidity rewards and maker rebates | Polymarket, from taker fees | Maker rebate 15% of taker fees on sports, 20% crypto, 25% on most other categories. Orders must rest at least 3.5 seconds and are sampled once a minute | Polygon non-revenue slice about €473,000 a day, rebates and rewards and referrals together | The rewards-only total. A 187-wallet sample (polyfees, 13 Oct 2026) had a typical liquidity-reward receipt of $49.66 over 30 days |
| Polymarket perps liquidity program | Polymarket perps | $75,000 a day, split across active markets, plus $1,000 on a market’s first day | €67,000 budgeted | Whether a non-KYC wallet can join. DefiLlama’s perp volume for Polymarket is 100% off-chain. Eligibility is 1% of trailing seven-day maker volume, with a $100,000 credited-notional cap per tier |
| UMA proposer on Polymarket | The market’s reward | About $2 per undisputed correct proposal. Polyflux counted 162,197 of ~179,700 settlements paying exactly $752, which is a $750 bond plus $2. Some markets pay up to $5, a few up to $20 | Not found as a daily total | A daily proposal count. The bond is $500–$750, and $25,000–$50,000 on the large political markets |
| Kleros juror | The party who files the dispute | General Court: 0.005 ETH per coherent vote. At $2,343/ETH (Coinlib, 25 Oct 2026) that is €10.46. Other courts publish 0.0007–0.064 ETH | Not found | Cases per day, and total PNK staked, so a draw probability is impossible |
| The Graph indexer | Query payers | Query fees, of which indexers, delegators, and curators take the supply side | $38 in the last 24 hours, $17,920 over 30 days, about €530 a day | Current daily GRT issuance paid on top of query fees |
| CoW solver | CoW DAO, in COW | Weekly, for bid quality and for quotes. Onboarding doc describes evaluation, a bonding pool, and a KYC step | Bitquery: 36.8 million COW paid in 2026 year to date. Their dollar conversion uses a thin COW price they flag themselves, so I am not converting it | A clean euro-per-day figure |
| Across relayer | The user, inside the bridge fee | Gas plus capital cost. A Risk Labs Dune page shows relayers at roughly 2–6 bps | DefiLlama says $2,448 in 24 hours and $71,406 over 30 days, against $211 million and $5.87 billion of volume. Those fees are too small for a 2–6 bp charge. The two sources do not reconcile | A trustworthy daily relayer payroll |
| Boundless, Succinct, Fermah provers | Whoever orders a proof | Boundless: median $0.04 per billion cycles, capacity 400 trillion cycles a day (Boundless blog, 19 Oct 2026). Capacity is not spend | Succinct: the provers visible on one Dune query for 1 Oct 2026 sum to about $1,370. The query may be truncated. Fermah publishes no fees | Actual daily dollars paid on Boundless and Fermah |

Chainlink, Pyth, and RedStone publishers are permissioned. I did not find a daily payout figure for ERC-4337 bundlers. Bundling is an inclusion race, so it fails the “correctness, not arrival” test anyway. Optimistic-rollup challengers get paid when a fraud proof wins. I found no daily payout, because honest chains produce none.

## 4. The killer, per item

* Crypto perp CLOBs, HIP-3 stock and commodity perps, Ondo perps if permissionless, Lighter and the other new perp venues: toll exceeds gross at this latency, and the size that would matter requires capital.
* Ostium FX and commodities, HIP-4 outcomes, the whole options category, Panoptic, The Graph’s query fees: pie too small. Ostium’s entire fee average is about €3,900 a day. HIP-4’s is about €2,100. Options are about €11,600. The Graph is about €530.
* Boros, Across relaying, CoW solving, proof marketplaces: requires capital, or hardware, or both. Proof races also go to the fastest GPU, so they fail the correctness test.
* Polymarket international from Italy, Polymarket US, Kalshi, Securitize and Franklin and BUIDL-style funds, CoW’s solver set, Chainlink-style oracle seats, HIP-3 deployment itself: closed by construction. Italy is geoblocked and ISP-blocked on Polymarket. The UMA proposer role is about to close further: Risk Labs is blocking on-chain proposals around 11 Nov 2026 and routing them through its own API, because proposers were being front-run.
* Kleros is the exception on capital. At $0.008293 per PNK (Yahoo, 25 Oct 2026), the General Court’s 2,300 PNK minimum is about €17, inside €52. The draw is stake-weighted, and the daily case count is unpublished.

## 5. The straight answer

No item here has a documented path to €10 a day for this profile, and none has a documented path from there to €500 a day. The large pools, Hyperliquid at roughly €2.3 million a day of fees and trade.xyz at roughly €200,000, are tolls. A one-second account pays them.

Kleros comes closest, and only on a per-vote basis. One coherent General Court vote pays about €10.46, the stake fits, and the clock is days rather than milliseconds. Without a published case rate and a published total stake, the expected day is unknown and, because draws scale with stake, a €17 stake is the thin end of it. That cannot be stretched to €500 a day without staking far more PNK than €52.

Two numbers I would still want measured, and could not find: Kleros cases per day against total PNK staked in the General Court, and the rewards-only line inside Polymarket’s €473,000 Polygon distribution. Neither measurement changes the capital and access gates above.
