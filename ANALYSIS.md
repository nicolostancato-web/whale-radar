# 🔬 DATA_ANALYST — materia prima per il loop
*2026-08-20 06:04 UTC · 131 token tradeabili · correlazione != causa*

## (a) Feature attuali: chi porta segnale?
| feature | forza (0.5=nulla) | media vincenti | media morti |
|---|---|---|---|
| sell_ratio | 0.72 | 0.89 | 1.18 |
| log_n_firstbuyers | 0.67 | 1.60 | 1.19 |
| dump_depth | 0.61 | 38.06 | 6.99 |
| log_volume | 0.57 | 4.88 | 5.07 |
| log_buy_accel | 0.56 | -0.23 | -0.01 |
| smart_money_frac | 0.53 | 0.11 | 0.15 |
| ore_flow | 0.50 | 5.21 | 6.65 |

## (b) Wallet candidati smart-money (first-buyer su ≥3 token, alto tasso di vittoria)
| wallet | vinti/token | tasso |
|---|---|---|
| `0xa55bc8f356f7…` | 3/3 | 100% |
| `0x1e03fa0a2d55…` | 3/3 | 100% |
| `0xddb4549ded45…` | 3/3 | 100% |
| `0x6bf0e60c9f53…` | 3/3 | 100% |
| `0x52817f455bf3…` | 3/3 | 100% |
| `0x39447263e0ce…` | 3/4 | 75% |
| `0x90924c7d483c…` | 3/4 | 75% |
| `0xf55915820a27…` | 3/4 | 75% |

→ **46 wallet** con ≥60% di vincite su ≥3 token = candidati per una feature 'segue-gli-smart' (da validare no-lookahead).

## (c) I MOSTRI (picco ≥6x): 25/131 token — cosa avevano all'entrata
- **ore_flow** PIÙ BASSO nei mostri (4.04 vs 6.75)
- **sell_ratio** PIÙ BASSO nei mostri (0.91 vs 1.14)
- **log_buy_accel** PIÙ BASSO nei mostri (-0.27 vs -0.03)
- **dump_depth** PIÙ BASSO nei mostri (12.63 vs 16.80)
- **smart_money_frac** PIÙ BASSO nei mostri (0.07 vs 0.15)
- **log_n_firstbuyers** PIÙ ALTO nei mostri (1.64 vs 1.23)

> Questi sono CANDIDATI, non verità. La prossima leva del loop si pesca da qui,
> si costruisce come feature, e si testa in EDGE_EVAL (walk-forward onesto).