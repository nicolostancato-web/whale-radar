# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 17 workflow attivi*

## 🔴 5 PROBLEMI
- **database**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **engine**: 5 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **loop0**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **ricerca**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **sperimenti**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 1 AUTO-FIXATI
- repo_gc #14: chiuso, era appeso da 63.5h e bloccava la corsia

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 3.0h fa |
| ✅ | collector | success | 2.7h fa |
| 🟡 | database | pending | 1.3h fa |
| 🟡 | engine | in_progress | 0.5h fa |
| ✅ | heartbeat | success | 3.0h fa |
| ✅ | insider | success | 400.1h fa |
| ✅ | ispezione | success | 0.3h fa |
| 🟡 | loop0 | in_progress | 0.6h fa |
| ✅ | paper_bot | success | 0.2h fa |
| ✅ | repo_gc | success | 13.4h fa |
| 🟡 | ricerca | in_progress | 1.1h fa |
| ✅ | solana_helius | success | 2.0h fa |
| 🟡 | sperimenti | pending | 1.5h fa |
| ✅ | storico | in_progress | 1.6h fa |
| ✅ | strategy_optimizer_solana | success | 416.0h fa |
| ✅ | vivo | in_progress | 1.2h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.