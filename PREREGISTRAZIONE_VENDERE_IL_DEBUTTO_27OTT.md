# Pre-registration — selling the debut — 27 Oct, written before the test

## The rule, fixed now

- **Universe**: USDT perpetual futures on Binance, newly listed.
- **Event**: the symbol's first hour of trading.
- **Entry**: **short**, at the close of the **first full hour** — not the first
  print, which cannot be obtained.
- **Exit**: **72 hours** later.
- **Costs included**: 0.10% (2 legs) plus the **funding actually paid or
  received by the short** over the holding period.
- **A debut is genuine only if** its first timestamp is not shared with 3 or
  more other symbols. A shared start date is the floor of my downloader, not
  an event in the world — this error was made twice today before the detector
  was written.

## What has been measured in sample

133 debuts, 2025-2026.

| | 24h | **72h** | 168h |
|---|---|---|---|
| price only | +4.02% ± 3.78 | +7.67% ± 4.12 | +4.90% ± 8.28 |
| funding (short's side) | −0.84% ± 0.45 | −1.27% ± 0.69 | −1.65% ± 0.87 |
| **net** | +3.08% ± 3.82 | **+6.30% ± 4.02** | +3.15% ± 8.32 |
| median | +5.59% | +6.12% | +9.37% |
| winners | 68% | 68% | 66% |

Only 72h clears zero. Mean and median agree, and removing the three worst
cases **improves** the mean (+9.59% vs +7.57% before funding) — so this is not
a few lucky outliers, it is broad.

Worst single position: **−86.8%**. Funding worst case: **−25.7%**.

## The test, fixed before running

Binance lists roughly 747 USDT perpetuals; 336 are on disk. The remaining
~400 have **never been touched** by this search and are different subjects,
not the same subjects on another venue — the distinction that killed the
previous candidate this morning.

**Pass requires all three:**
1. net return at 72h **positive with its interval excluding zero**;
2. winners **above 55%**;
3. the mean **not driven by the tail** — removing the 3 best must leave it
   positive.

**Fail:** any of the three. Then this joins the register of closed roads.

## Known weaknesses, stated in advance

- The 72-hour horizon was **chosen after seeing** 24/72/168. The
  pre-registration fixes it; it does not undo the selection. That is precisely
  what the held-out sample is for.
- Shorting has unbounded loss. Even if it passes, no position may exceed a
  few per cent of capital, and the −86.8% case must be assumed to recur.
- Borrow availability and the ability to actually open a short in the first
  hour of a new listing have **not** been verified.

---

# OUTCOME — same day, run exactly as written above

**FAILED.** 365 held-out debuts (6 excluded on a shared start date).

| | in sample (133) | held out (365) |
|---|---|---|
| net at 72h | +6.30% ± 4.02 | **−1.87% ± 4.12** |
| median | +6.12% | +4.81% |
| winners | 68% | 62% |
| without the 3 best | +9.59% (before funding) | **−2.42%** |
| worst case | −86.8% | **−344.3%** |

| bar | result |
|---|---|
| 1. above zero, interval excluding it | **NO** |
| 2. winners above 55% | PASSES |
| 3. not driven by the tail | **NO** |

## What actually happened

The shape is the classic one for selling a pump: **it wins often and loses
catastrophically**. 62% winners and a positive median, and a negative mean,
because one coin out of 365 rose 345% in three days and ate the profit of all
the others. The 133-coin sample simply did not contain such a case.

Reality is worse than the arithmetic: a −344% move liquidates the position
long before the 72 hours are up, so that number is not even reachable — the
loss is capped at the margin, and the position is gone.

## What is deliberately NOT being done

A stopped version — exit at −30% — is an obvious thought, and it is **not
being tested on this sample**. Running it here would consume the only clean
data left and produce a calibrated number dressed as a validated one. If that
variant is ever worth pursuing it needs a fresh population of its own.

## What this cost and what it bought

Four hours. It bought the strongest-looking candidate of the project being
killed **before** any money touched it, by a bar written down in advance. The
in-sample +6.30% was real, measured correctly, net of fees and funding — and
still wrong about the future.
