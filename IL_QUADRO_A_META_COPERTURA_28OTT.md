# The picture at 42% coverage — 28 Oct

255 events, 231 occasions, 25.3 effective days.

## First, a correction that changed the sign

Every euro figure before this used **my own price assumptions**, and they
were wrong: wstETH was priced as ETH, rETH and cbETH likewise, sDAI as a
dollar. They are worth **1.25×, 1.17× and 1.14×** respectively — the oracle
says wstETH is $2,898 against WETH's $2,323.

Understating the collateral made dozens of liquidations look like **losses**,
and the total premium came out **negative (−€37,903)** while the positive
ones alone summed to €201,456. That contradiction is what exposed it.

The fix is better than a hand-corrected table: prices are now read from
**Aave's own oracle** — the same price the protocol uses to decide
liquidations. No price is assumed anywhere now, and all 231 occasions are
valuable instead of 176.

## The numbers

| | |
|---|---|
| occasions | **9.1 per day** |
| median occasion | **€0.40** — dust |
| over €100 | 45 (1.78/day), €337,750 |
| **over €1,000** | **24 (0.95/day), €331,408** |
| over €5,000 | 8 (0.32/day), €296,836 |
| five largest | €98,150 · €79,010 · €52,085 · €17,817 · €16,600 |
| **total, all liquidators** | **€10,843 per day** |

## Who takes it

| | |
|---|---|
| distinct liquidators | **72** across 231 occasions |
| share of the busiest | **8%** |
| top three together | 21% |
| **winners of the 24 occasions over €1,000** | **20 different addresses** |

**There is no dominant player.** Twenty different winners across twenty-four
large occasions is the opposite of a monopoly, and the opposite of what I
expected when I assumed professional bots would own this.

## Concentration in time

| best days | share of value |
|---|---|
| 1 | 56% |
| 3 | **99%** |

## Where this stands

About **one strike a day worth over a thousand euros**, taken each time by
someone different, in a field of seventy where nobody rules. Coverage is 42%
and every number here has moved as coverage grew — so these are the current
best estimates, not conclusions.
