# 🧠 LEARNER — il sistema impara dai propri trade
*2026-09-05 14:46 UTC*

Esempi etichettati: **60** (vincenti 14, perdenti 46)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.68** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **smart_money_frac**: +1.09  ＋ alza P(vincita)
- **sell_ratio**: +0.88  ＋ alza P(vincita)
- **log_volume**: +0.81  ＋ alza P(vincita)
- **log_n_firstbuyers**: +0.76  ＋ alza P(vincita)
- **ore_flow**: -0.34  － abbassa P(vincita)
- **log_buy_accel**: -0.24  － abbassa P(vincita)
- **dump_depth**: +0.18  ＋ alza P(vincita)

✅ **Selezione ATTIVA**: AUC 0.68 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.