# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 13 workflow attivi*

## 🔴 3 PROBLEMI
- **engine**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **loop0**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **sperimenti**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 1 AUTO-FIXATI
- **ricerca**: fermo da 3.1h → RI-LANCIATO ✅

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 3.3h fa |
| ✅ | collector | success | 1.6h fa |
| 🟡 | engine | pending | 3.3h fa |
| ✅ | heartbeat | success | 3.3h fa |
| ✅ | insider | success | 304.0h fa |
| ✅ | ispezione | success | 0.2h fa |
| 🟡 | loop0 | pending | 1.3h fa |
| ✅ | paper_bot | success | 0.1h fa |
| ✅ | repo_gc | success | 3.3h fa |
| 🔧 | ricerca | pending | 3.1h fa |
| 🟡 | sperimenti | pending | 1.7h fa |
| ✅ | strategy_optimizer_solana | success | 319.9h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.