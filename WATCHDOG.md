# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 15 workflow attivi*

## 🔴 4 PROBLEMI
- **engine**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **loop0**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **sperimenti**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **storico**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 1 AUTO-FIXATI
- repo_gc #14: chiuso, era appeso da 44.1h e bloccava la corsia

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 5.8h fa |
| ✅ | collector | success | 5.5h fa |
| ✅ | database | in_progress | 0.8h fa |
| 🟡 | engine | pending | 1.3h fa |
| ✅ | heartbeat | success | 5.8h fa |
| ✅ | insider | success | 380.7h fa |
| ✅ | ispezione | success | 3.7h fa |
| 🟡 | loop0 | in_progress | 3.4h fa |
| ✅ | paper_bot | success | 0.2h fa |
| ✅ | repo_gc | queued | 44.1h fa |
| ✅ | ricerca | pending | 1.5h fa |
| 🟡 | sperimenti | in_progress | 1.6h fa |
| 🟡 | storico | in_progress | 0.2h fa |
| ✅ | strategy_optimizer_solana | success | 396.6h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.