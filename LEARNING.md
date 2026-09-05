# 🧠 LEARNER — il sistema impara dai propri trade
*2026-09-05 07:12 UTC*

Esempi etichettati: **81** (vincenti 17, perdenti 64)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.68** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **log_n_firstbuyers**: +1.05  ＋ alza P(vincita)
- **log_volume**: +0.64  ＋ alza P(vincita)
- **sell_ratio**: +0.54  ＋ alza P(vincita)
- **smart_money_frac**: +0.26  ＋ alza P(vincita)
- **ore_flow**: -0.19  － abbassa P(vincita)
- **log_buy_accel**: +0.15  ＋ alza P(vincita)
- **dump_depth**: -0.09  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.68 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.