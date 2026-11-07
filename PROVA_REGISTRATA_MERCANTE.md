# Pre-registration — the two-minute merchant

Written **before** the forward test runs. Nothing below may be changed once the
first opportunity is logged. Any change starts a new test with a new name.

## The rule

- **Universe**: every pool initialised on Robinhood Chain (PoolManager
  `0x8366a39c…`) with declared fee `10000` (1.00%) and hook `0x0` (no hook).
- **Eligibility**: the pool must have had at least one swap before entry. No
  other filter. No selection on volume, name, creator, or anything knowable
  after entry.
- **Entry**: at the end of the first minute after the pool's first swap.
- **Position**: EUR 52 equivalent (0.0157 ETH), full-range, our share capped at
  50% of measured depth.
- **Exit**: exactly **2 minutes** after entry. Not at a target, not on a signal.
- **Costs**: 2 transactions of gas at the measured rate, subtracted always.
- **Accounting**: net = √(P_exit/P_entry) − 1 + fees_collected/capital − gas.
  If no sell print exists after entry, the position counts as **−100%**.
- **No position is removed afterwards for any reason**, including missing data.

## What would make it a success

Pre-declared, so it cannot be moved later:

- **Primary**: mean net per position > **+0.5%** with a 95% interval that
  excludes zero, over at least **200 positions**.
- Reported alongside: median, share of positions at −100%, and the gas share.
- The calibration row: pools that saw **zero swaps** during the two minutes must
  come out at **exactly −gas**. If they come out positive, the table is
  unreadable and the test is void.

## What would kill it

- mean ≤ 0, or an interval that contains zero after 200 positions;
- more than 20% of positions at −100%;
- the in-archive result (+1.5% ± 0.8) failing to reproduce within its interval.

## Why this test and not another

Eight previous strategies died on the toll. This is the first measurement taken
from the side that **collects** the toll rather than pays it. The archive says
+1.5% ± 0.8 at two minutes on 1.00% pools, over 5,023 coins with no selection;
the same table is +0.0% on 0.30% pools, so the whole result lives on the fee
tier, and 53% of live pools carry it.

**Known weakness, stated in advance:** the archive measurement assumes we obtain
our share of in-range liquidity for the full two minutes. Sixty-three merchants
are already doing this. If they crowd the active tick, our realised share is
smaller than modelled and the result shrinks toward zero.
