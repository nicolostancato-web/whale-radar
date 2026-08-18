# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-18 13:03 UTC*

Esempi etichettati: **118** (vincenti 36, perdenti 82)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.70** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.34  － abbassa P(vincita)
- **log_volume**: -0.85  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.73  ＋ alza P(vincita)
- **ore_flow**: -0.64  － abbassa P(vincita)
- **dump_depth**: +0.48  ＋ alza P(vincita)
- **smart_money_frac**: -0.30  － abbassa P(vincita)
- **log_buy_accel**: -0.24  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.70 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.