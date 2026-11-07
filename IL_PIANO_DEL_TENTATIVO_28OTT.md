# The plan for an attempt — 28 Oct, full coverage

**This is a plan, not an action.** Putting a contract on-chain that moves
real money is Nicolò's decision, not mine.

## Final numbers, 100% coverage, 58.7 effective days

| | |
|---|---|
| occasions | **4.9 per day** |
| total value, all liquidators | **€5,219 per day** |
| **value not guarded by repeat actors** | **€2,958 per day** |
| concentrated in | wstETH, sUSDe, WBTC — **86%** |
| occasions over €1,000 | 0.48 per day |
| largest observed | €98,150 |

## What has to be built

**1. The contract** (~150 lines of Solidity)
Receives a flash loan of the debt asset, calls `liquidationCall`, swaps the
seized collateral, repays the loan, keeps the difference.

The safety property that matters: **it must revert unless the profit exceeds
a threshold set inside the contract**. Then the worst case of any bug, any
lost race, any price move mid-transaction is a **reverted transaction costing
cents of gas**. The contract holds no funds between operations, so there is
nothing to steal from it.

**2. The watcher**
Reads health factors each block and triggers when one drops below 1. Measured
capacity on free public nodes: **6 reads/second, ~72 positions per block** —
enough if the watch list stays in the hundreds.

**3. The list of positions to watch** — *this is the real unknown*
To know whose health to check, the set of borrowers is needed. Aave does not
expose it; it must be built from historical `Borrow` events, and the free
archive we have (Blockscout) is rate-limited to 5 windows per run. Building
the list is days of patient collection, not an afternoon.

## Costs

| | |
|---|---|
| deploying the contract | **~€0.20** at current gas |
| each failed attempt | **cents** |
| flash loan | 0.05% of the borrowed amount, read from the contract |
| unwinding the collateral | 0.01–0.23% measured at €200,000 |
| monthly running cost | **€0** — free public nodes |

**Total to try: under one euro.** This is the first thing in this entire
search where the cost of finding out is smaller than the cost of discussing
it.

## What can go wrong, honestly

1. **We lose every race.** Most likely outcome on the crowded assets. The
   plan is to compete only where the repeat actors are absent.
2. **The niche closes.** Somebody configures wstETH tomorrow and €80,000 of
   unguarded value becomes guarded.
3. **The measurements are of the past.** Sixty days of history say nothing
   binding about the next sixty.
4. **A contract bug.** Mitigated by the revert-unless-profitable rule, and by
   testing against a local fork of the chain before anything goes live.
5. **sUSDe and rsETH rest on one occasion each.** Only wstETH (19 occasions)
   and WBTC (16) are solid legs.

## What I propose

Build it, test it on a **local fork** where no real money exists, and bring
the result back before anything touches the chain. That stage costs **zero
euro and zero risk**, and answers the one question measurement cannot: does
the whole sequence actually execute.

Going live afterwards is a separate decision, and it is yours.
