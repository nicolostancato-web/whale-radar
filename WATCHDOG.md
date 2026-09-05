# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 12 workflow attivi*

## 🔴 2 PROBLEMI
- **loop0**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **ricerca**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 3.0h fa |
| ✅ | collector | success | 2.8h fa |
| ✅ | engine | in_progress | 0.9h fa |
| ✅ | heartbeat | success | 3.0h fa |
| ✅ | insider | success | 154.0h fa |
| ✅ | ispezione | success | 0.2h fa |
| 🟡 | loop0 | in_progress | 0.9h fa |
| ✅ | paper_bot | success | 0.2h fa |
| ✅ | repo_gc | success | 18.2h fa |
| 🟡 | ricerca | cancelled | 3.7h fa |
| ✅ | strategy_optimizer_solana | success | 169.9h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.