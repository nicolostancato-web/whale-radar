# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-22 06:55 UTC*

Esempi etichettati: **157** (vincenti 43, perdenti 114)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.78** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.32  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.89  ＋ alza P(vincita)
- **log_volume**: -0.76  － abbassa P(vincita)
- **ore_flow**: -0.68  － abbassa P(vincita)
- **log_buy_accel**: -0.55  － abbassa P(vincita)
- **dump_depth**: +0.51  ＋ alza P(vincita)
- **smart_money_frac**: -0.34  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.78 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.