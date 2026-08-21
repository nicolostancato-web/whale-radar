# 🧠 LEARNER — il sistema impara dai propri trade
*2026-08-21 18:51 UTC*

Esempi etichettati: **146** (vincenti 40, perdenti 106)

## Performance out-of-sample (media multi-split, onesta): AUC = **0.74** (0.5 = caso)
## Cosa predice un vincente (peso appreso dai dati, non da me):
- **sell_ratio**: -2.38  － abbassa P(vincita)
- **log_n_firstbuyers**: +0.86  ＋ alza P(vincita)
- **ore_flow**: -0.65  － abbassa P(vincita)
- **log_volume**: -0.58  － abbassa P(vincita)
- **dump_depth**: +0.49  ＋ alza P(vincita)
- **log_buy_accel**: -0.43  － abbassa P(vincita)
- **smart_money_frac**: -0.30  － abbassa P(vincita)

✅ **Selezione ATTIVA**: AUC 0.74 ≥ 0.6. Il bot entra solo sui token
con alta P(vincita) secondo il modello appreso. Si ri-allena ad ogni giro.