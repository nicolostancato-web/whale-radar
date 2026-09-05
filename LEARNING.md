# 🧠 LEARNER — il sistema impara dai propri trade
*2026-09-05 09:57 UTC*

Esempi etichettati: **71** (vincenti 18, perdenti 53)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.70** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **log_n_firstbuyers**: +1.05  ＋ alza P(vincita)
- **log_volume**: +0.58  ＋ alza P(vincita)
- **smart_money_frac**: +0.53  ＋ alza P(vincita)
- **ore_flow**: -0.43  － abbassa P(vincita)
- **dump_depth**: +0.31  ＋ alza P(vincita)
- **sell_ratio**: +0.26  ＋ alza P(vincita)
- **log_buy_accel**: -0.11  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.70 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.