# 🧠 LEARNER — il sistema impara dai propri trade
*2026-09-05 11:03 UTC*

Esempi etichettati: **69** (vincenti 17, perdenti 52)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.57** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: +1.00  ＋ alza P(vincita)
- **log_n_firstbuyers**: +0.92  ＋ alza P(vincita)
- **smart_money_frac**: +0.62  ＋ alza P(vincita)
- **log_volume**: +0.55  ＋ alza P(vincita)
- **ore_flow**: -0.38  － abbassa P(vincita)
- **log_buy_accel**: -0.19  － abbassa P(vincita)
- **dump_depth**: +0.09  ＋ alza P(vincita)

⚠️ **Selezione non ancora attiva**: AUC 0.57 < 0.6.
Il modello continua ad accumulare/allenarsi finche' non trova un segnale affidabile.