# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-20 01:47 UTC*

Esempi etichettati: **129** (vincenti 37, perdenti 92)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.73** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.21  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.90  ＋ alza P(vincita)
- **log_volume**: -0.86  － abbassa P(vincita)
- **ore_flow**: -0.69  － abbassa P(vincita)
- **dump_depth**: +0.55  ＋ alza P(vincita)
- **log_buy_accel**: -0.47  － abbassa P(vincita)
- **smart_money_frac**: -0.29  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.73 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.