# 📊 REPORT FASE 2 — INSIDER (2026-08-15, double-double deep-search)

## Verdetto: confidenza BASSA (segnale fat-tail, non robusto)
Dataset: 5.949 balene arricchite, esito 72h, **solo 62 token** (aneddotico, <soglia 40 valida ma piccolo).

**Feature singole (72h per-token, media | mediana):** direzionalmente TUTTE giuste
- early_quiet +2.7% | -37.5%  (vs NON-early -25.9%)
- token giovane +14.7% | -39.4%
- prime 3 balene +47.8% | -27.9%
- comprato basso +25.0% | -28.6%  (vs comprato alto -27.1%)

**Score composito (0-4) OUT-OF-SAMPLE:** FALLISCE
- score alto (>=3): -42.3% (23 token) — peggio del basso
- score basso (<=1): -37.8%

**Tensione:** feature singole promettenti MA mediane negative (fat-tail: pochi mostri) + composito overfit OOS + campione piccolo.

## Osservazioni per la FASE 1 (dal deep-search)
1. Espandere a 200-300 token (62 aneddotici)
2. **First-buyers VERI**: wallet che comprano nei primi minuti dal listing, NON solo balene >=$3k (la soglia taglia i piccoli insider!)
3. Funding size dalla forense (finanziato da entita' grossa)
4. Timing preciso (blocchi dal listing) + liquidita'/depth all'entrata

## Score robusto (per la prossima Fase 2)
Walk-forward temporale per token (non split random), regolarizzazione L1/L2, max 3-4 feature non collineari,
pesatura per liquidita', target Sharpe non rendimento grezzo, validazione portafoglio >=40 token nel test.

## Prossima analisi
Portafoglio simulato sulle feature migliori (first-mover + comprato-basso) su 100+ token non sovrapposti,
entry/exit precise + stop -15%, per misurare se la CODA DESTRA (i mostri) e' replicabile o rumore.
