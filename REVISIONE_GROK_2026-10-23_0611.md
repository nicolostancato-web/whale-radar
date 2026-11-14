# Revisione Grok — 2026-10-23 06:11 UTC

Modello grok-4.7, sforzo high. Costo: ZERO (abbonamento, nessuna chiave API).
Tempo: 361s

---

The on-chain pattern is a free receipt through one program, then a pump.fun sale. I’ll identify that program and the wallets from public docs and posts, then separate open distributions from insider allocations.This channel is closed. The receipts you measured are claims from a named-recipient vesting escrow. The selling wallets were written into those escrows by the creator. A new wallet with a few hundred euros cannot add itself.

## 1. The program is Jupiter Lock

`LocpQgucEQHbqNABEYvBvwoxCPsSbG91A1QaQhQQqjn` is **Jupiter Lock**, a public token-locking and vesting program. Jupiter’s developer docs name that program id, point the code at `jup-ag/jup-lock`, and the interface is [lock.jup.ag](https://lock.jup.ag/). Audits cited there are OtterSec and Sec3. There is no protocol fee, only the Solana network fee and account rent.

Meteora uses the same deployment. The `@meteora-ag/met-lock-sdk` package documents that exact mainnet address, and the IDL checked into [MeteoraAg/dynamic-bonding-curve](https://github.com/MeteoraAg/dynamic-bonding-curve/blob/main/idls/locker.json) is named `locker` at that address. Jupiter’s launch flow on Meteora’s dynamic bonding curve calls it when a creator locks a slice of supply. A July 2025 note from @crodiewifpills records that for `$VIBE` (20%) and `$CATDET` (5%), with the lock accounts owned by this program. In March 2025 @AISUEDE listed the same address among “long term escrow contracts.”

Anyone can create a lock. Each lock has exactly one recipient, chosen by the creator at creation. Only that recipient can claim, and the claim is manual. The schedule (cliff, cliff amount, vesting duration, frequency) is fixed. Cancel and “change the recipient” exist only if the creator granted them at the start. Default is neither.

That matches the transactions. A claim is signed by the recipient. The locker moves tokens from the escrow’s token account to the recipient and, if needed, the associated-token-account program creates the recipient’s token account in the same transaction. The SOL spent is rent plus the network fee. It is not a purchase of the tokens. The wallet you called the owner (`GU63SH4…`, `3XDcE2tQ…`) is the escrow creator: the wallet that already held the tokens and named the recipient.

The two instructions are:

| Instruction | Discriminator (first 8 bytes) | Who signs | What it means |
|---|---|---|---|
| `claim` | `62, 198, 214, 193, 213, 159, 108, 210` | `recipient`, and that key must equal `escrow.recipient` | Named beneficiary withdraws what has vested |
| `claim_v2` | `229, 87, 46, 162, 21, 157, 231, 114` | same | Same claim, SPL Token and Token-2022 |

The IDL also has `create_vesting_escrow_from_root`, which opens a personal escrow for someone who presents a merkle proof against a root the project published. Your receipts do not look like that. The tokens are attributed to one creator wallet per mint, and two recipient wallets share the same odd amounts. That is “one lock per recipient,” which is how this program pays a list the creator typed in.

On pump.fun there is no separate creator mint. Coins sold through `6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P` come off the bonding curve. So the economic source sits one hop earlier: the creator wallet bought or otherwise took the tokens from the curve, then locked them to `B6jqNwTJ…` and `BegDtqRj…`. The selling wallets’ books show a gift because the buy is on the other address. The repeated sizes (532,876 / 571,256 / 407,964) are what periodic vesting looks like. The fields to read on the escrow are `cliff_time`, `cliff_unlock_amount`, `frequency`, `amount_per_period`, and `number_of_period`.

Pasting `B6jqNwTJNyZPEeXFdoYuxGWeEtM2FX9dX7ZmzjovaVHg` into lock.jup.ag shows every lock where it is recipient or creator, including creator, cliff, and amount already claimed. That lookup is free.

## 2. The wallets are not a known public operation

Web and X search on `B6jqNwTJ…`, `BegDtqRj…`, `GU63SH4oyp…`, and `3XDcE2tQRo…` returns no posts, no explorer write-ups, and no public label. They are not attached, in anything indexed, to a bot service, a launchpad brand, or a KOL roster.

The program id is discussed. The wallets are not. Two of the X hits on the program id are misreadings of it as a person’s wallet (a December 2024 reply to a caller, and a February 2025 LIBRA theory). It is the program.

Same amounts, overlapping mints, two recipient addresses, and one creator per mint is one operator splitting claims across two keys. A public airdrop does not pay two private wallets the same awkward quantities.

## 3. What is actually open, with about €300 and no relationship

Ranked by how little access it requires. None of these reproduce the 53 SOL result.

| Programme | Open to a newcomer? | What arrives | What it costs | Scale on ~€300 |
|---|---|---|---|---|
| Jupiter Lock claim, as in these transactions | Only if a creator typed your address into the escrow | The meme token | Rent and a fee, if you were named. You cannot name yourself into someone else’s escrow | The whole 53 SOL. Closed |
| JitoSOL or another liquid stake | Yes | Staking yield | The SOL you stake. Solana Compass quoted 5.10% APY on its own liquid-stake product on 22 Oct 2026 | On the order of €15 a year |
| Jupiter Active Staking Rewards | Yes, for the next quarter, if you stake in time | JUP, pro-rata | For the Jul–Sep 2026 round: a time-weighted average of at least 50 JUP over the whole quarter. Claims for that round opened 12 Oct 2026 at [jup.ag/rewards/asr-2026-q3](https://jup.ag/rewards/asr-2026-q3). Earning closed 30 Sep 2026, so today is too late for it. Pool is 50 million JUP. Voting is not required | A minimum stake earns a thin slice. Paid in JUP, after the quarter |
| pump.fun Holder Rewards | Yes, on coins launched in that mode | The quote asset (SOL, USDC, or PUMP), several times an hour, pro-rata | Buy and hold more than $20 of that coin. The position can go to zero. About 12% of new launches were in this mode in an early-October sample | A rebate on volume, against the price of the coin |
| pump.fun app referral match | Yes, under the published rules | Up to $50 for the referrer and $50 for the new user, in installments | A real new user, fiat deposit through the app’s payment provider, then trades on 5 distinct days inside 10. The deposit alone pays nothing. Cap is the deposit or $50, whichever is smaller. Terms dated 7 Oct 2026 at [pump.fun/docs/referral-rewards](https://pump.fun/docs/referral-rewards). One reward per person, one wallet, UK excluded | $50 if you personally qualify once. Nothing further without real new users |
| Creator fees on a coin you launch | Anyone can create a coin | 0.30% of bonding-curve volume to the creator wallet; after graduation a market-cap tier that write-ups in Sep–Oct 2026 put between 0.95% and 0.05% | Creating is free. Income exists only if strangers trade | This is launching, which you already classed as closed for the purpose of receiving |
| Kamino Season 6, Seeker/SKR, generic “points” | No current open claim | — | SKR claims closed in April 2026 and required a Seeker phone. No Kamino Season 6 had been announced as of mid-October 2026 | €0, and deposit-for-points has no published conversion |

Jupiter Lock can also run a merkle distribution (`create_root_escrow`, then `create_vesting_escrow_from_root`). That is open only when the project published the eligibility rule before the root existed and the claimant set is large. It is still a list the project built. There is no standing Jupiter Lock campaign a stranger can join.

## 4. What pump.fun pays for, live now

pump.fun does not hand the meme token to people who perform an action.

- **Creator fee.** Paid in the quote asset to the creator wallet. Since 9 Jan 2026 the creator can split that fee across up to 10 wallets, transfer ownership, or revoke update authority. Those wallets are named by the creator.
- **Holder Rewards**, introduced 12–13 Sep 2026 when Cashback stopped being a launch option. On those coins the creator fee is diverted to holders of more than $20, paid in the quote asset, automatically. Pump’s own [holder-rewards notes](https://github.com/pump-fun/pump-public-docs/blob/main/docs/HOLDER_REWARDS_README.md) describe `distribute_fee_to_holders`, signed by pump’s holder-reward authority. The inbound asset is SOL, USDC, or PUMP. It will not show up as a `Locp` transfer of the meme mint, and the recipient already holds the coin.
- **Cashback** still exists only on old coins. New launches choose Creator Fee or Holder Rewards.
- **App referral and callout rewards**, announced 16 Oct 2026 by @Pumpfun. The match is the $50 schedule above. The other half is a cut of app trading fees, with a temporary 4× boost for referrers, and a referred user’s app fee cut from 0.45% to about 0.40%. This is a rebate for using the app, not an allocation of the coin being traded.

The 27% of pump.fun selling that comes from wallets that never bought that mint is this structure at scale: the buy, the bundle, or the curve inventory sits on wallet A, and wallet B is a vesting recipient, a fee-share wallet, or a plain transfer destination. The Base 32% is the same economic fact on that chain’s launch contracts. I did not re-decode Base in this pass. The same test applies there: identify the program that emitted the free receipt, then see whether the recipient was named by one creator or admitted by a public proof.

## 5. The on-chain signature that separates the two

Decode the instruction, then count recipients.

**Internal allocation, which is what these trades are**

- Program `Locp…`, instruction `claim` or `claim_v2`.
- Escrow field `recipient` equals the selling wallet, and `creator` equals the wallet that funded it (`GU63SH4…`, `3XDcE2tQ…`).
- One creator, one to a handful of recipients per mint. Those recipients share a SOL funding source.
- The creator wallet has an earlier buy or a first position on `6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P` for the same mint.
- Claim sizes line up with `amount_per_period`.

**Still internal, even on the merkle path**

- `create_vesting_escrow_from_root` against one `root_escrow`, but only a few dozen leaves, or the claimants were all funded by the creator. A private list is still a private list. The error string `InvalidMerkleProof` in this IDL only means a proof was checked. It does not mean the list was public.

**Open distribution**

- One root, or one distributor, and hundreds or thousands of recipient wallets with unrelated funding histories.
- The eligibility rule was published before the root’s creation slot: a snapshot of holders, stakers, or phone owners.
- Or the inflow is not the meme token at all. Jupiter ASR pays JUP from Jupiter’s rewards distributor to wallets that staked. Pump holder rewards pay the quote asset from pump’s authority to wallets that hold more than $20. Both fail the “received the meme token, never bought it” screen, because one requires a prior JUP stake and the other requires holding the coin.

A plain SPL transfer from the deployer, with no escrow and no proof, is inventory moved between the operator’s own wallets.

## 6. What to refuse

- **Any claim site that is not the program’s own interface.** Lock claims are at lock.jup.ag. ASR is at jup.ag/rewards. The referral terms are at pump.fun/docs/referral-rewards. A “claim your $PUMP” post that sends people to a lookalike domain is a wallet drain. Connecting a wallet and signing an unknown transaction is the loss.
- **Paid presales.** pump.fun has no presale. “Send SOL, receive the allocation” is a transfer to the asker’s wallet.
- **Farming points, or a season that has not been announced.** Kamino has no Season 6 announcement to join. A points balance with no published token and no published rate is a cost with an unnamed payoff.
- **Buying Holder Rewards coins in order to collect the fee.** The fee is a thin cut of volume. The $20 position is the part that can go to zero.
- **Self-referral on the $50 match.** The terms require one natural person, one wallet, a user who has never used pump.fun, and a review before each installment. Five days of meme trading can cost more than the $50, and a second account voids it.
- **Tokens that cannot be sold.** Freeze authority still on, a permanent delegate, the non-transferable extension, a transfer fee near 100%, or a pool with nothing on the other side. Jupiter’s own lock docs say the escrow does not care if the token later has no market. The claim still succeeds, and the tokens are unsellable.
- **A RugCheck “locked supply” badge treated as safety.** RugCheck has displayed Jupiter Lock positions since September 2024. A lock whose recipient is the creator’s second wallet, whose cliff has already passed, or which the creator can still cancel, is the arrangement in your sample. The badge and the dump are the same escrow, read at two different times.

The position that survived inspection is the creator paying themselves on a second address, then selling. It is reachable only by being that creator, or by being a wallet that creator chose to name.
