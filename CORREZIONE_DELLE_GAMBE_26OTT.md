# Correction: I counted two legs where there were four — 26 Oct

A pair trade is **four** commissions, not two: open the long, open the short,
close the long, close the short. I used 0.10% throughout where the true cost is
**0.20%**. The same applies to the cross-market reversal (long one quintile,
short another).

| strategy | gross | **true cost** | corrected net | what I reported |
|---|---|---|---|---|
| mechanically-linked pairs, all 435 | +0.020% | 0.200% | **−0.180%** | −0.069% |
| cross-market reversal, 72h→12h | +0.116% | 0.200% | **−0.084%** | +0.016% to +0.076% |
| attention, fade at 4h | +0.146% | 0.100% | +0.046% | +0.046% *(this one was right)* |

## Two things I told Nicolò that were wrong

**The cross-market reversal was never positive.** I spent hours on it, called it
"the only thing that replicated across two venues", and debated whether maker
fills could rescue it. It was negative from the start, because it pays four
commissions and I was counting two. The cross-venue replication remains a fact;
the economics never were.

**"The gross and the toll have nearly touched" was false.** The toll was double.
They never came close.

## The error class

A constant assumed rather than counted. I wrote `0.0010 = two legs` at the top
of a script and carried it through an entire day without once asking how many
legs a pair position actually has. Third time this week: the invented 0.30%
fee, the assumed 0.06% maker advantage, now the leg count.

**The rule that would have caught all three: a constant that enters a result
must be derived in the file where it is used, with its derivation written
beside it.** Not imported, not remembered, not reasonable-looking.

No conclusion changes — everything was already negative and is now more so. But
for a full day I believed we were closer than we were.

---

## Audit of every cost constant in the codebase

Three more understatements found, all the same shape:

| file | was | should be | why |
|---|---|---|---|
| price patterns on 19 markets | 0.05% | **0.10%** | one leg counted, a round trip has two |
| cross-sectional, commodities and stocks | 0.10% | **0.20%** | long-short is four legs |
| mechanically-linked pairs | 0.036% | **0.072%** | a pair is four legs |

**Three of four understated by exactly half.** Not carelessness — one mental
pattern repeated.

**No verdict changes.** Everything was already negative and is now more so; the
pairs test still returns zero results above zero with the doubled cost.

Every cost constant now carries its derivation in the file that uses it: how
many legs, at what rate, on which venue. A number at the top of a script with
no line deriving it is a suspect, even one I wrote yesterday.
