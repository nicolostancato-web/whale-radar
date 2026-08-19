# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-19 18:49 UTC*

Esempi etichettati: **128** (vincenti 37, perdenti 91)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.75** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.20  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.90  ＋ alza P(vincita)
- **log_volume**: -0.84  － abbassa P(vincita)
- **ore_flow**: -0.68  － abbassa P(vincita)
- **dump_depth**: +0.54  ＋ alza P(vincita)
- **log_buy_accel**: -0.46  － abbassa P(vincita)
- **smart_money_frac**: -0.31  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.75 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.