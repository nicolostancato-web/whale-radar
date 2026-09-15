# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 17 workflow attivi*

## 🔴 6 PROBLEMI
- **database**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **engine**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **loop0**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **ricerca**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **sperimenti**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **storico**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 1 AUTO-FIXATI
- repo_gc #14: chiuso, era appeso da 60.5h e bloccava la corsia

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 4.3h fa |
| ✅ | collector | success | 4.2h fa |
| 🟡 | database | pending | 0.3h fa |
| 🟡 | engine | in_progress | 0.1h fa |
| ✅ | heartbeat | success | 4.3h fa |
| ✅ | insider | success | 397.1h fa |
| ✅ | ispezione | success | 0.2h fa |
| 🟡 | loop0 | pending | 1.0h fa |
| ✅ | paper_bot | success | 0.2h fa |
| ✅ | repo_gc | success | 10.4h fa |
| 🟡 | ricerca | pending | 0.6h fa |
| ✅ | solana_helius | success | 2.3h fa |
| 🟡 | sperimenti | in_progress | 1.1h fa |
| 🟡 | storico | in_progress | 1.8h fa |
| ✅ | strategy_optimizer_solana | success | 413.0h fa |
| ✅ | vivo | in_progress | 0.8h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.