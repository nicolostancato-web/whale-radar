# 🔬 DATA_ANALYST — materia prima per il loop
*2026-08-22 07:15 UTC · 157 token tradeabili · correlazione != causa*

## (a) Feature attuali: chi porta segnale?
| feature | forza (0.5=nulla) | media vincenti | media morti |
|---|---|---|---|
| sell_ratio | 0.73 | 0.87 | 1.13 |
| log_n_firstbuyers | 0.64 | 1.62 | 1.19 |
| dump_depth | 0.63 | 33.97 | 6.02 |
| log_volume | 0.58 | 4.88 | 5.13 |
| log_buy_accel | 0.58 | -0.29 | 0.09 |
| ore_flow | 0.51 | 5.16 | 6.32 |
| smart_money_frac | 0.51 | 0.11 | 0.15 |

## (b) Wallet candidati smart-money (first-buyer su ≥3 token, alto tasso di vittoria)
| wallet | vinti/token | tasso |
|---|---|---|
| `0xa55bc8f356f7…` | 3/3 | 100% |
| `0x1e03fa0a2d55…` | 3/3 | 100% |
| `0xddb4549ded45…` | 3/3 | 100% |
| `0x6bf0e60c9f53…` | 3/3 | 100% |
| `0x52817f455bf3…` | 3/3 | 100% |
| `0xe71a69f434a7…` | 4/5 | 80% |
| `0x39447263e0ce…` | 3/4 | 75% |
| `0x90924c7d483c…` | 3/4 | 75% |

→ **48 wallet** con ≥60% di vincite su ≥3 token = candidati per una feature 'segue-gli-smart' (da validare no-lookahead).

## (c) I MOSTRI (picco ≥6x): 30/157 token — cosa avevano all'entrata
- **ore_flow** PIÙ BASSO nei mostri (4.37 vs 6.39)
- **sell_ratio** PIÙ BASSO nei mostri (0.88 vs 1.10)
- **log_buy_accel** PIÙ BASSO nei mostri (-0.33 vs 0.06)
- **dump_depth** PIÙ BASSO nei mostri (10.94 vs 14.32)
- **smart_money_frac** PIÙ BASSO nei mostri (0.08 vs 0.15)
- **log_n_firstbuyers** PIÙ ALTO nei mostri (1.66 vs 1.23)

> Questi sono CANDIDATI, non verità. La prossima leva del loop si pesca da qui,
> si costruisce come feature, e si testa in EDGE_EVAL (walk-forward onesto).