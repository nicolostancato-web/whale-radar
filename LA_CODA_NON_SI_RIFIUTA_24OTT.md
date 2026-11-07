# The tail cannot be refused in advance — 24 Oct

The merchant's result is destroyed by 1.15% of coins that die inside the window
and cost −100%. If those could be declined before entry, the net would go from
+0.32% to nearly +2%. They cannot.

Threshold chosen on the first half of the archive, tested on the second half,
never seen:

| criterion, known at minute one | first half | second half (unseen) |
|---|---|---|
| no filter | −0.68% ± 1.29 | −0.24% ± 1.04 |
| ≥20 swaps | −0.26% ± 1.33 | −0.15% ± 1.04 |
| ≥5 sell prints | −0.51% ± 1.29 | −0.20% ± 1.04 |
| pre-entry volume ≥ 2 ETH | **−0.24% ± 1.45** | **−0.47% ± 1.16** |

The best filter on the first half is the **worst** on the second. The
improvement was the search, not the signal.

*(Absolute levels here are lower than elsewhere because this run used pre-entry
volume as the depth proxy instead of the impact estimate, which understates
fees. The comparison between filters is unaffected, and that is the point.)*

**Verdict: the merchant trade stays where it was — about +0.3% central at small
size, negative at EUR 5,000 — and without a working filter it is not a machine.**
Ninth variant closed.

## Next: the only candidate with a structural reason rather than a statistical hope

Robinhood Chain carries **tokenized equities** (NVDA and others seen among quote
assets). The US cash market closes; the token keeps trading all night. Whoever
buys NVDA at 03:00 pays a wide spread **because the exchange is shut** — and
that spread does not rest on a pattern that can evaporate. It rests on a clock.
