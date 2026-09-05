# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 12 workflow attivi*

## 🔴 3 PROBLEMI
- **engine**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **loop0**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **ricerca**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 6.1h fa |
| ✅ | collector | success | 5.8h fa |
| 🟡 | engine | in_progress | 0.6h fa |
| ✅ | heartbeat | success | 6.1h fa |
| ✅ | insider | success | 146.4h fa |
| ✅ | ispezione | success | 1.8h fa |
| 🟡 | loop0 | in_progress | 1.8h fa |
| ✅ | paper_bot | success | 0.2h fa |
| ✅ | repo_gc | success | 10.5h fa |
| 🟡 | ricerca | in_progress | 0.2h fa |
| ✅ | strategy_optimizer_solana | success | 162.3h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.