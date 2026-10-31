# Seven seconds — the first real data point — 30 Oct

The notebook caught its first event, and it is the most important number the
project has produced.

```
22:54:40   we see it liquidatable     (health 0.9947, was 1.0044)
22:54:47   someone else liquidates    (block 26301520)
           ↑
       SEVEN SECONDS AFTER US
```

**We saw the position seven seconds before the winner acted.** Building and
sending a transaction takes us about **0.2 seconds**.

| | |
|---|---|
| position | 0xc593352e… |
| debt at the moment it fell | $11,510 |
| collateral | $14,932 |
| liquidated by | 0x0b79a21dd0e6b3… |
| debt after | $7,780 — a **partial** close, about a third |
| premium actually taken | roughly **$150** |

Had the system been armed, **this one was winnable**.

## The reservations, because it is one observation

- **One event is not a statistic.** This may have been a position nobody was
  watching closely.
- **The premium was small**: ~$150 real, not the $460 theoretical on the
  whole debt.
- **Unknown whether our transaction would have succeeded** — we had the time,
  but we also needed the right sale route for that collateral.
- **Clocks**: ours is the Mac's, theirs is the block's. They can differ by
  seconds — but not by seven.

## Status on the four questions

| | |
|---|---|
| **1. System alive** | yes — 2,026 cycles, 250 minutes. But the guardian restarted it **40 times**: the monitor keeps dying. It works, but on a crutch that needs explaining. |
| **2. Falls observed** | **one**, caught cleanly |
| **3. How long the window lasted** | **at least 7 seconds** — the number that was missing, and it points our way |
| **4. Could we have been there** | **yes, with 35× the margin needed** |

This does not prove we can win. It proves the window exists and that on this
occasion it was wide. The next ones will say whether that was luck.
