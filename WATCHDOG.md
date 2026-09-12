# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 13 workflow attivi*

## 🔴 4 PROBLEMI
- **engine**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **loop0**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **ricerca**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **sperimenti**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 6.8h fa |
| ✅ | collector | success | 2.1h fa |
| 🟡 | engine | in_progress | 2.8h fa |
| ✅ | heartbeat | success | 2.5h fa |
| ✅ | insider | success | 310.9h fa |
| ✅ | ispezione | success | 1.6h fa |
| 🟡 | loop0 | pending | 0.7h fa |
| ✅ | paper_bot | success | 0.1h fa |
| ✅ | repo_gc | success | 10.2h fa |
| 🟡 | ricerca | in_progress | 2.0h fa |
| 🟡 | sperimenti | in_progress | 0.5h fa |
| ✅ | strategy_optimizer_solana | success | 326.8h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.