# 🧠 LEARNER — il sistema impara dai propri trade
*2026-09-05 21:13 UTC*

Esempi etichettati: **77** (vincenti 19, perdenti 58)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.57** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **log_n_firstbuyers**: +1.07  ＋ alza P(vincita)
- **smart_money_frac**: +0.47  ＋ alza P(vincita)
- **log_volume**: +0.45  ＋ alza P(vincita)
- **ore_flow**: -0.28  － abbassa P(vincita)
- **dump_depth**: +0.25  ＋ alza P(vincita)
- **sell_ratio**: +0.16  ＋ alza P(vincita)
- **log_buy_accel**: +0.11  ＋ alza P(vincita)

⚠️ **Selezione non ancora attiva**: AUC 0.57 < 0.6.
Il modello continua ad accumulare/allenarsi finche' non trova un segnale affidabile.