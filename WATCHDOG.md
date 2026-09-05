# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 12 workflow attivi*

## 🔴 2 PROBLEMI
- **loop0**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **ricerca**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 4.5h fa |
| ✅ | collector | success | 4.2h fa |
| ✅ | engine | pending | 1.4h fa |
| ✅ | heartbeat | success | 4.5h fa |
| ✅ | insider | success | 140.3h fa |
| ✅ | ispezione | success | 0.4h fa |
| 🟡 | loop0 | pending | 3.2h fa |
| ✅ | paper_bot | success | 0.3h fa |
| ✅ | repo_gc | success | 4.5h fa |
| 🟡 | ricerca | pending | 1.5h fa |
| ✅ | strategy_optimizer_solana | success | 156.2h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.