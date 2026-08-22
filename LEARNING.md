# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-22 15:31 UTC*

Esempi etichettati: **158** (vincenti 42, perdenti 116)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.75** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.30  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.86  ＋ alza P(vincita)
- **log_volume**: -0.78  － abbassa P(vincita)
- **ore_flow**: -0.67  － abbassa P(vincita)
- **log_buy_accel**: -0.54  － abbassa P(vincita)
- **dump_depth**: +0.52  ＋ alza P(vincita)
- **smart_money_frac**: -0.31  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.75 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.