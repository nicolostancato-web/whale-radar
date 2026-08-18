# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-18 18:53 UTC*

Esempi etichettati: **120** (vincenti 35, perdenti 85)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.67** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.11  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.87  ＋ alza P(vincita)
- **log_volume**: -0.83  － abbassa P(vincita)
- **ore_flow**: -0.66  － abbassa P(vincita)
- **dump_depth**: +0.53  ＋ alza P(vincita)
- **log_buy_accel**: -0.40  － abbassa P(vincita)
- **smart_money_frac**: -0.29  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.67 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.