# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 15 workflow attivi*

## 🔴 3 PROBLEMI
- **engine**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **ricerca**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **sperimenti**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 1 AUTO-FIXATI
- repo_gc #14: chiuso, era appeso da 50.9h e bloccava la corsia

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | in_progress | 0.0h fa |
| ✅ | collector | success | 6.5h fa |
| ✅ | database | pending | 1.5h fa |
| 🟡 | engine | pending | 0.7h fa |
| ✅ | heartbeat | success | 0.0h fa |
| ✅ | insider | success | 387.5h fa |
| ✅ | ispezione | success | 4.3h fa |
| ✅ | loop0 | pending | 0.8h fa |
| ✅ | paper_bot | success | 0.2h fa |
| ✅ | repo_gc | success | 0.8h fa |
| 🟡 | ricerca | pending | 0.6h fa |
| 🟡 | sperimenti | pending | 0.0h fa |
| ✅ | storico | in_progress | 0.4h fa |
| ✅ | strategy_optimizer_solana | success | 403.4h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.