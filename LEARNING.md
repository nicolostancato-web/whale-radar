# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-18 06:59 UTC*

Esempi etichettati: **117** (vincenti 36, perdenti 81)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.69** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.34  － abbassa P(vincita)
- **log_volume**: -0.82  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.74  ＋ alza P(vincita)
- **ore_flow**: -0.63  － abbassa P(vincita)
- **dump_depth**: +0.48  ＋ alza P(vincita)
- **smart_money_frac**: -0.30  － abbassa P(vincita)
- **log_buy_accel**: -0.24  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.69 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.