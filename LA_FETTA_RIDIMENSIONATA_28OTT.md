# The slice, counted by actor — six times smaller — 28 Oct

This afternoon's figure said non-professionals win 85% of the value,
€6,911/day, and that the largest premium in the dataset — €98,150 — was
taken by an address appearing exactly once.

**Counted by actor instead of by contract, that is wrong.**

## Resolving every liquidator to its creator

77 liquidator addresses → **45 distinct creators** (rotation factor 1.56).
Shared deployment factories were excluded first: the Foundry deterministic
deployer appears as "creator" for unrelated people's contracts, and would
have merged strangers into one actor.

| | by contract | **by actor** |
|---|---|---|
| distinct subjects | 65 | **49** |
| value to repeats (3+) | 15% | **55%** |
| value to the rest | 85% — €6,911/day | **45% — €3,648/day** |
| actors with exactly one occasion | €2,981/day | **€449/day** |

## The €98,150 was a professional after all

It is no longer in the one-occasion group: **its creator has other
occasions**. It was a professional using a fresh contract — precisely the
alternative explanation I raised and then had to run before believing
anything. On that specific case, what I told Nicolò this afternoon was
wrong, and this is the correction.

## Where the candidate stands now

Still alive, with a much smaller prize:

- true no-man's-land (actors appearing once): **~€450/day**
- grey zone contested by low-activity actors: **~€3,600/day**
- the professional core: ~€4,500/day, not reachable by us

The structure of the finding survives — no capital gate, no auction, deep
liquidity on the awkward collateral — but the headline number shrinks by a
factor of **6.6**, and it shrank because the unit of counting was wrong.
That is the fourth time in two days that the unit was the error.
