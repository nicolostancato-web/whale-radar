# 🔬 DATA_ANALYST — materia prima per il loop
*2026-08-21 07:26 UTC · 143 token tradeabili · correlazione != causa*

## (a) Feature attuali: chi porta segnale?
| feature | forza (0.5=nulla) | media vincenti | media morti |
|---|---|---|---|
| sell_ratio | 0.72 | 0.89 | 1.16 |
| log_n_firstbuyers | 0.66 | 1.61 | 1.17 |
| dump_depth | 0.63 | 35.56 | 6.55 |
| log_buy_accel | 0.55 | -0.23 | 0.02 |
| log_volume | 0.55 | 4.95 | 5.07 |
| ore_flow | 0.53 | 4.98 | 6.53 |
| smart_money_frac | 0.51 | 0.12 | 0.14 |

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

→ **47 wallet** con ≥60% di vincite su ≥3 token = candidati per una feature 'segue-gli-smart' (da validare no-lookahead).

## (c) I MOSTRI (picco ≥6x): 27/143 token — cosa avevano all'entrata
- **ore_flow** PIÙ BASSO nei mostri (4.04 vs 6.56)
- **sell_ratio** PIÙ BASSO nei mostri (0.91 vs 1.12)
- **log_buy_accel** PIÙ BASSO nei mostri (-0.27 vs 0.00)
- **dump_depth** PIÙ BASSO nei mostri (12.00 vs 15.53)
- **smart_money_frac** PIÙ BASSO nei mostri (0.08 vs 0.15)
- **log_n_firstbuyers** PIÙ ALTO nei mostri (1.65 vs 1.21)

> Questi sono CANDIDATI, non verità. La prossima leva del loop si pesca da qui,
> si costruisce come feature, e si testa in EDGE_EVAL (walk-forward onesto).