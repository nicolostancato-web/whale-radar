# 🔬 DATA_ANALYST — materia prima per il loop
*2026-08-26 07:29 UTC · 210 token tradeabili · correlazione != causa*

## (a) Feature attuali: chi porta segnale?
| feature | forza (0.5=nulla) | media vincenti | media morti |
|---|---|---|---|
| sell_ratio | 0.71 | 0.88 | 1.08 |
| log_n_firstbuyers | 0.69 | 1.62 | 0.95 |
| dump_depth | 0.61 | 30.89 | 7.74 |
| smart_money_frac | 0.56 | 0.11 | 0.12 |
| log_volume | 0.53 | 4.91 | 5.04 |
| log_buy_accel | 0.53 | -0.12 | 0.22 |
| ore_flow | 0.50 | 5.94 | 6.09 |

## (b) Wallet candidati smart-money (first-buyer su ≥3 token, alto tasso di vittoria)
| wallet | vinti/token | tasso |
|---|---|---|
| `0xa55bc8f356f7…` | 3/3 | 100% |
| `0x52817f455bf3…` | 3/3 | 100% |
| `0x2e209a99c452…` | 3/3 | 100% |
| `0xfeed63662e80…` | 3/3 | 100% |
| `0x6bf0e60c9f53…` | 3/3 | 100% |
| `0xca7c8b739f26…` | 3/3 | 100% |
| `0x30ba0ed08879…` | 3/3 | 100% |
| `0x1e03fa0a2d55…` | 3/3 | 100% |

→ **37 wallet** con ≥60% di vincite su ≥3 token = candidati per una feature 'segue-gli-smart' (da validare no-lookahead).

## (c) I MOSTRI (picco ≥6x): 35/210 token — cosa avevano all'entrata
- **ore_flow** PIÙ BASSO nei mostri (4.66 vs 6.33)
- **sell_ratio** PIÙ BASSO nei mostri (0.88 vs 1.06)
- **log_buy_accel** PIÙ BASSO nei mostri (-0.16 vs 0.20)
- **dump_depth** PIÙ BASSO nei mostri (11.17 vs 13.67)
- **smart_money_frac** PIÙ BASSO nei mostri (0.08 vs 0.12)
- **log_n_firstbuyers** PIÙ ALTO nei mostri (1.65 vs 1.00)

> Questi sono CANDIDATI, non verità. La prossima leva del loop si pesca da qui,
> si costruisce come feature, e si testa in EDGE_EVAL (walk-forward onesto).