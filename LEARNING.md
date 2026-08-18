# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-18 21:34 UTC*

Esempi etichettati: **124** (vincenti 36, perdenti 88)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.75** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.10  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.90  ＋ alza P(vincita)
- **log_volume**: -0.78  － abbassa P(vincita)
- **ore_flow**: -0.62  － abbassa P(vincita)
- **dump_depth**: +0.54  ＋ alza P(vincita)
- **log_buy_accel**: -0.40  － abbassa P(vincita)
- **smart_money_frac**: -0.34  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.75 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.