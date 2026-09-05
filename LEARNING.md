# 🧠 LEARNER — il sistema impara dai propri trade
*2026-09-05 06:04 UTC*

Esempi etichettati: **81** (vincenti 19, perdenti 62)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.64** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **log_n_firstbuyers**: +0.92  ＋ alza P(vincita)
- **smart_money_frac**: +0.55  ＋ alza P(vincita)
- **sell_ratio**: +0.45  ＋ alza P(vincita)
- **log_volume**: +0.36  ＋ alza P(vincita)
- **ore_flow**: -0.20  － abbassa P(vincita)
- **dump_depth**: -0.11  － abbassa P(vincita)
- **log_buy_accel**: +0.10  ＋ alza P(vincita)

✅ **Selezione ATTIVA**: AUC 0.64 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.