# Cross-venue arbitrage — opened and closed in one hour, 27 Oct

The same coin trades on Binance and on Hyperliquid. If the two prices drift
apart by more than the 0.19% toll of a four-leg position, there is a trade.
The data was already on disk, which is why this road was picked: shortest
time-to-know.

## The divergence is real

39 coins, 191,295 matched hours. Median |divergence| 0.045%, 99th percentile
0.346%. **5.32% of hours exceed the 0.19% toll**, and on some coins far more
often — RSR 30%, DYDX 29%, IOTA 25%.

Alignment was verified first: at zero offset the median is 0.0451%, at ±1 hour
0.353%. The archives match on the instant, so the divergence is not an
artefact of mismatched clocks.

## And it is not buyable

The signal is the hourly close. Entering **at that same close** gives
+0.47% net per operation at a 0.5% trigger. Entering **one hour later**, which
is the earliest an order can actually be sent after seeing the close:

| trigger | enter at the signal (impossible) | enter one hour later (real) |
|---|---|---|
| 0.2% | +0.0517% ± 0.0067 | **−0.1901% ± 0.0072** |
| 0.3% | +0.1989% ± 0.0147 | **−0.1954% ± 0.0166** |
| 0.5% | +0.4700% ± 0.0371 | **−0.1710% ± 0.0446** |

Every cell lands on −0.19%, which is the toll itself. **Gross profit is zero.**
The whole apparent edge was look-ahead: the spread closes inside the very hour
in which it is observed, so by the time an order could be placed there is
nothing left to collect.

## What it leaves behind

Not nothing. It says the deviation's lifetime is **under one hour**. If an
arbitrage exists between these venues it belongs to the speed architecture —
competing on latency against professionals — which was already closed with
numbers. So this is not a road that needs better data; it is a road that ends
where it starts.

Cost of finding out: one hour, zero euro. That is what the triage rule
(shortest time-to-know first) is for.
