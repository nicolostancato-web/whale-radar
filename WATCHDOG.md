# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 16 workflow attivi*

## 🔴 5 PROBLEMI
- **engine**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **loop0**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **ricerca**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **sperimenti**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **storico**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 1 AUTO-FIXATI
- repo_gc #14: chiuso, era appeso da 56.2h e bloccava la corsia

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 5.2h fa |
| ✅ | collector | success | 4.9h fa |
| ✅ | database | pending | 1.8h fa |
| 🟡 | engine | pending | 0.7h fa |
| ✅ | heartbeat | success | 5.2h fa |
| ✅ | insider | success | 392.7h fa |
| ✅ | ispezione | success | 3.7h fa |
| 🟡 | loop0 | in_progress | 1.7h fa |
| ✅ | paper_bot | success | 0.2h fa |
| ✅ | repo_gc | success | 6.0h fa |
| 🟡 | ricerca | pending | 0.8h fa |
| ✅ | solana_helius | success | 1.6h fa |
| 🟡 | sperimenti | in_progress | 1.0h fa |
| 🟡 | storico | in_progress | 2.3h fa |
| ✅ | strategy_optimizer_solana | success | 408.7h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.