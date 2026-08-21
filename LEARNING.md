# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-21 21:35 UTC*

Esempi etichettati: **152** (vincenti 42, perdenti 110)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.71** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.35  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.89  ＋ alza P(vincita)
- **log_volume**: -0.69  － abbassa P(vincita)
- **ore_flow**: -0.65  － abbassa P(vincita)
- **dump_depth**: +0.49  ＋ alza P(vincita)
- **log_buy_accel**: -0.48  － abbassa P(vincita)
- **smart_money_frac**: -0.37  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.71 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.