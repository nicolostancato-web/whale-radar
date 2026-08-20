# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-20 13:06 UTC*

Esempi etichettati: **134** (vincenti 41, perdenti 93)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.77** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.60  － abbassa P(vincita)
- **log_volume**: -0.76  － abbassa P(vincita)
- **ore_flow**: -0.73  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.73  ＋ alza P(vincita)
- **dump_depth**: +0.47  ＋ alza P(vincita)
- **log_buy_accel**: -0.38  － abbassa P(vincita)
- **smart_money_frac**: -0.25  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.77 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.