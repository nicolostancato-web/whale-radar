# Revisione Grok — 2026-10-19 03:13 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 851s

---

The €24 mean is the only number that makes this look like a business, so I'm going to attack that number directly: how it was computed, who actually paid it, and how many launches it takes before it shows up in a bank account.The €24.41 is not a sampling fluke, and it is not the expectation of a €1.71 launch. It is the average of a mixture whose euros sit in a few coins, and on this factory the coins that trade are the ones whose creator named up to 32 extra wallets in the launch transaction. Those wallets pay creator tax and are not the launcher, so your split booked them as customers.

I re-read the live factory at block 92,288,889 (a handful of free `eth_call`s, €0). `launchFee()` is 0.0005 ETH, `maxCreatorTaxBps()` is 1000, `snipeTaxStartBps()` is 9900, `snipeTaxSeconds()` is 3, `launchEnabled()` is true, and `canLaunch` on a random address is true. Public launching is open right now. It is one owner bit.

`CurveBuy(address indexed buyer, address indexed recipient, uint256 quoteIn, uint256 tokensOut, uint256 fee, uint256 tax)` puts creator tax in data word 3. Word 2, `fee`, is the 1% curve fee with the opening snipe tax folded in. Your 31% zeros and ~2% of quote is the right word. The snipe tax is not inside the €24.41.

## 1. The artefact

Creator tax is charged on every buy, including buys from addresses the launcher listed as snipe-tax exempt. The factory exempts the launching address and the fee recipient automatically, and `launchToken` takes up to 32 more. The list is fixed in the launch transaction and emits `SnipeTaxExempted`. The tax is keyed on the **recipient**, not the sender. A bundler contract is `buyer`; the exempt wallets are `recipients`. Excluding "the launcher" misses both.

That list is the product. Arrow sells a Pons bundler. The documented industrial pattern is: waive the 99% opening tax for 15–25 wallets, and one or three blocks later one transaction buys for all of them. Those buys still pay creator tax. Your classifier calls every one of them "others." A round trip of that tax returns to the creator on claim and is not income. The only external cash in the trade is the protocol's cut of the 1% fee, which flows the other way.

The shape of the sample is what that mechanism produces. The bottom 70% can contribute at most 5% of the euros even if every one of them earned the full €1.71 (350 × 1.71 / 12,205). The top 10 coins are 58% of the sum. Median €0.01 is what a launch with no bundle and no buyer looks like, and that is  the bulk of the 424,571.

The query, on the 500 you already have:

Join each launch to its transaction. Take the exempt set as the launcher, `creatorFeeRecipient`, every `SnipeTaxExempted` address, and every address in the `snipeTaxExemptions` argument. Flag a `CurveBuy` when `recipient` or `buyer` is in that set, when the buy shares a transaction with two or more recipients, or when the buyer was funded by the launcher or an exempt address in the same block or the 20 before it. Report flagged tax over total tax, and the same ratio on the top decile of curves. Then split the 500 into plain launches (value exactly 0.0005 ETH, empty exemption list, no `launchAndBuy`) versus everything else, and report the mean and the share of euros in each cell.

If the plain cell is ~€0 and the top decile is mostly flagged, the €24.41 is the launcher paying himself. That query costs reads you can already do. It dominates the €1.71 experiment.

Check the max coin in the same pass. €1,629 is 0.54 ETH. At the 10% cap that is roughly one graduation of buys, not a mysterious whale. If `tax/quoteIn` on that curve equals its `creatorTaxBps` on every fill, the decode is fine and the concentration is real. If one fill carries the whole sum, the decode is the artefact instead.

## 2. The mean is real arithmetic. It is not a bank balance.

Your figures are internally consistent. Sum at €24.41 × 500 is €12,205. Dropping the top 10 leaves a mean of €10.48, so those ten hold €7,070. Sample standard deviation is about €115. Standard error is about €5. A 95% interval of €14.86–€35.61 is the ordinary interval for that sample. Nobody mis-computed a bootstrap.

It is the wrong object.

The top 2% holding 58% of the sum implies a tail index around 1.2 (the single max alone, 13% of the sum, implies something nearer 1.5). Between 1 and 2 the mean exists and the variance does not. The bootstrap resamples the coins you saw. It cannot draw a coin larger than €1,629, and the error of the mean then shrinks like n to the power of about −0.17, not −0.5. So the interval is narrower than the uncertainty on the **next** 500. That is a real defect. It is the smaller one. "Within 50% of the mean" is a wide band, €12–€37, and the ordinary interval already fits inside it.

I rebuilt a 500-point distribution that matches your median, your 70% below €1.71, P75, P90, the max, the ex-top-10 mean and the overall mean, and resampled campaigns from it. Treating those 500 as the true distribution you will actually draw from:

| Launches | Median realised average | Share of campaigns inside €12–€37 | Share with average above €1.71 |
|---|---|---|---|
| 1 | €0 | ~4% | 30% |
| 10 | ~€12 | ~30% | ~80% |
| 20 | ~€15 | ~35% | ~94% |
| 100 | ~€23 | ~75% | ~all |
| 200 | ~€23 | ~90% | all |

So the honest count, **if every launch is an iid draw from that historical mixture**, is about 100 before three campaigns in four are inside ±50% of the mean, and about 200 before nine in ten are. You do not need thousands. Profitability against the €1.71 arrives earlier than closeness to the mean, because €10 already clears the cost.

That "if" is the entire claim, and it is false. The 500 include the bundled launches. A silent €1.71 launch is a draw from the plain cell in the query above. On the evidence you published, that cell lives at the median.

## 3. Why this has not been, and will not be, arbitraged by you

The marginal launch already earns about zero. That is the median, and 70% of launches fail to cover €1.71. Something like 5,000 launches a day are already taking the other side of this table (155,684 in the 30 days to 18 Oct 2026). Ninety percent of addresses try once. The cheap ticket has been bought.

What has not been competed away is the right tail, and the scarce input there is not 0.0005 ETH.

- **Attention.** The UI is the discovery channel, and it is a firehose. Buyers sort by activity. Activity at birth is the exempt bundle. A coin with no buy, no logo and no social is the median coin.
- **The bundle is the real cost.** The exemption cap is 32 wallets, fixed at creation, and those wallets have to buy. That inventory is the strategy. It is also the bag. Creator tax on it comes back on claim; the protocol's share of the 1% fee does not; the tokens are worth nothing if nobody follows. Pricing the strategy at €1.71 counts the postage and ignores the stake.
- **No lifetime launch cap.** One address launched 1,732 times, so the chain is not banning serial deployers. The bit that can stop you is `launchEnabled`, which is true today and is owner-mutable. The practical throttle is the UI burying you, not the factory reverting.
- **The buyer pool is the pool you already measured.** Pre-registered buy strategies lost money. Creator tax is a toll on those buyers. Pons fees have fallen from a peak near $4.9M in a day at the end of August to about $267k on 18 Oct 2026. A rising per-launch mean in your thirds, set against a collapsing chain-wide fee total, is what a mix shift toward higher `creatorTaxBps` or toward more self-bundling looks like. Split the thirds into average tax rate and average quote volume before calling it demand.
- **The fee recipient is revocable.** Fees accrue in escrow `0xd3AFEB2a57f70eF218Aa82451c51B2fb0416Ac9e` and are withdrawn. They are not pushed in the buy. The current recipient can be pointed elsewhere, and a creator who looks idle can be proposed off the fee stream by the protocol on a three-day timelock. The coins that matter are the ones worth taking.
- **Issuing is a different legal posture from trading.** You would be the named creator collecting a toll from buyers, on a chain operated by a US broker. That is the constraint that does not show up in a 500-row sample. Price it before the second launch, not after the hundredth.

## 4. What one coin can actually settle

It can settle whether `tax` is withdrawable by the recipient. It cannot settle the €24. A silent launch has a base rate near €0.01 under your own median, so a dead coin is the expected observation whether the mean is real or not. Watching the launcher's ETH balance across the buy will show nothing even when the tax is real, because the credit lands in `creatorTaxBalance` on the curve and then in the escrow. Your balance-delta test is aimed at the wrong account. The contract that holds €148.69 after a single transaction is what a fee recipient looks like: credits arrive as internal transfers and never increment the nonce. Read its internal transfers from the escrow on Blockscout. That check is free and uses the coin you already flagged.

For the €1.71, pre-register it as a routing test:

1. In the launch block, re-read `canLaunch`, `launchFee`, `maxCreatorTaxBps`.
2. Launch with `creatorTaxBps = 200`, buyback off, `creatorFeeRecipient` set to your EOA, empty socials, empty exemption list, value exactly 0.0005 ETH.
3. From a second wallet, after the 3-second window, buy a fixed 0.001 ETH. Phantom reserve on these curves is 1.68 ETH, so the price impact is dust. `fee/quoteIn` should be ~1% and `tax/quoteIn` ~2%. That separates the two pipes on a coin you control.
4. Read `creatorTaxBalance()` and the escrow balance for your recipient. Then `sweepFees` and claim. Claimed ETH should equal the `tax` field in full, plus the creator's share of `fee`. If the tax stays behind and only the base-fee share arrives, the field you summed is not yours. If nothing arrives, this deployment does not pay the way the docs describe.
5. Sell the 0.001 ETH back. Net cost of the probe is the launch fee plus the protocol's piece of the 1% round trip, which is cents.
6. Leave it silent for 57 hours. Two million blocks at the current 103 ms block time is 57 hours, not a long life. Any `tax` from an address other than your two wallets is one draw from the silent-launch distribution. Compare it with €0.01.

Also sum, on the same 500, `CurveSell`'s tax word and the hook's `HookFeeCollected.taxAmount`. You counted buys on the curve only. Sells carry creator tax too, and after graduation the tax is charged by the Uniswap v4 hook, which never emits `CurveBuy`. Both omissions push a true external figure **up**. They do not rescue a figure whose payers are the creator's own list.

## 5. What I would ask before anyone signs

- The plain-versus-bundled split in section 1, before any launch. If the plain cell is ~€0, the proposal is over.
- Mean `creatorTaxBps` and mean `quoteIn` separately for the three time thirds. The €12.99 / €19.99 / €40.05 series is not a demand series until those two move apart.
- Whether `creatorFeeRecipient` on the top 20 equals the launcher. Storage slot 1 equalling `deployer()` answers a different question. The struct stores them as different fields, and a zero recipient defaults to the caller only at launch.
- Total creator-tax euros versus total base-fee euros on the same 500. DefiLlama-style totals attribute on the order of $200 per launch of all-in fees in the recent 30 days, and the creator's share of the 1% fee is a second pipe that pays even at a 0% creator tax. You measured the smaller, optional pipe, and you measured it gross of who paid it.
- Recompute one native unit at today's ETH price. 0.0005 ETH = €1.50 implies €3,000 per ETH. Spot is near $2,400. A consistent FX scales cost and revenue together and leaves the ratio alone. A mixed FX does not.

Do the exempt-set query on the 500. Launching one coin answers a question the escrow balance already answers, and it draws once from the part of the distribution that loses money.
