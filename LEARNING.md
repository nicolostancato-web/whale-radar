# 🧠 LEARNER — il sistema impara dai propri trade
*2026-09-05 13:43 UTC*

Esempi etichettati: **60** (vincenti 14, perdenti 46)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.69** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **smart_money_frac**: +1.06  ＋ alza P(vincita)
- **sell_ratio**: +0.95  ＋ alza P(vincita)
- **log_n_firstbuyers**: +0.80  ＋ alza P(vincita)
- **log_volume**: +0.80  ＋ alza P(vincita)
- **ore_flow**: -0.40  － abbassa P(vincita)
- **log_buy_accel**: -0.25  － abbassa P(vincita)
- **dump_depth**: +0.23  ＋ alza P(vincita)

✅ **Selezione ATTIVA**: AUC 0.69 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.