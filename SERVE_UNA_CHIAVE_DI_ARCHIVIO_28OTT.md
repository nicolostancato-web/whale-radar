# Blocked on two free minutes — 28 Oct

## Where the work stands

The liquidation candidate needs one number: **how often the large occasions
arrive**. One has been seen (€617 net); the other three were worth 59 cents
between them. A frequency cannot be estimated from one event.

## Why it cannot be measured today

Free public RPCs keep only the **most recent days** of logs. Measured, same
query size at four depths:

| node | now | 1 day ago | 7 days ago | 60 days ago |
|---|---|---|---|---|
| publicnode | OK | **OK** | fail | fail |
| llamarpc / drpc / payload / 1rpc | fail | fail | fail | fail |

It is a **retention** limit, not a rate limit — patience does not get around
it. The first attempt at 60-day history failed on 98% of windows, and the
failure counter is what stopped "zero large occasions in two months" from
being published as a finding. It would have been the opposite of the truth.

## The two ways forward

| | time | cost |
|---|---|---|
| keep accumulating forward | **~10 days** | €0 |
| a free archive key (Alchemy or Infura free tier) | **~20 minutes** | **€0** |

Alchemy's free tier is 300M compute units a month, no card required; Infura's
is comparable. Either covers this measurement many times over. **No payment
is involved** — the only thing needed is an account, which I cannot create.

This is the second item of its kind pending, alongside the free FRED key for
macro release timestamps. Both are two-minute asks that cost nothing.

The forward accumulator keeps running regardless, so the number arrives
either way — this only changes whether it arrives today or in ten days.
