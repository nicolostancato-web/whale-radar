# The road to live — four steps, three of them free — 28 Oct

## On keys: there is nothing usable

The six private keys in the credentials file exist, but **all six hold zero
ETH on Ethereum**. They belonged to the Robinhood chain, whose RPCs no longer
answer. Going live needs ETH on Ethereum mainnet, and we have none.

## The four steps

**1. Local fork test** — *free, no money exists*
Copy the chain onto the Mac, replay a liquidation that actually happened, and
verify the whole sequence: flash loan → liquidate → sell → repay → profit. A
bug in the contract surfaces here, where it costs nothing.

**2. Virtual live** — *free, and exactly what Nicolò described*
The watcher runs on real data in real time and **writes down what it would
have done**, sending nothing. One or two weeks. The output is a log: "we
would have attempted 14 times, with these premiums" — and it answers the only
question measurement cannot: do we arrive in time, or do the professionals
always beat us.

**3. One real attempt** — *cost: cents of gas*
Only if step 2 shows at least some occasions were within reach.

**4. Let it run** — only if step 3 works.

**Steps 1 and 2 need no money and no wallet.** They can start immediately.

## What is needed from Nicolò, and only for step 3

A **fresh wallet**, created for this, holding **€15–20 of ETH**. Not one of
his own.

The reason is not formality. A key that sits in a text file and is used by an
automated program must be treated as **already compromised**: one mistake of
mine, one bad log, one file synced where it should not be. With €20 of gas in
it, the worst case costs €20. With savings in it, the worst case is something
else.

And one property makes this safe: **the contract never holds funds**. Profit
leaves immediately to an address Nicolò chooses, which can be his real
wallet — because that one needs no key in any file.

**So: nothing is needed now.** Steps 1 and 2 are worth weeks of information
and cost zero. If step 2 says it is worth it, the ask is €20 to a new
address. If it says no, there is no ask at all.
