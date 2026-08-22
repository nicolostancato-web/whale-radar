# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-22 01:46 UTC*

Esempi etichettati: **154** (vincenti 43, perdenti 111)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.74** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.39  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.88  ＋ alza P(vincita)
- **log_volume**: -0.72  － abbassa P(vincita)
- **ore_flow**: -0.67  － abbassa P(vincita)
- **dump_depth**: +0.50  ＋ alza P(vincita)
- **log_buy_accel**: -0.49  － abbassa P(vincita)
- **smart_money_frac**: -0.35  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.74 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.