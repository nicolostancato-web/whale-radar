# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 24 workflow attivi*

## 🔴 6 PROBLEMI
- **censimento**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **coppie**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **database**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **nascite**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **riserve**: 5 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **vivo**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 3 AUTO-FIXATI
- **collector**: fermo da 5.6h → RI-LANCIATO ✅
- **ispezione**: fermo da 3.7h → RI-LANCIATO ✅
- **sentinella**: fermo da 4.3h → RI-LANCIATO ✅

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | queued | 0.0h fa |
| ✅ | assottiglia | success | 68.0h fa |
| 🟡 | censimento | in_progress | 0.1h fa |
| 🔧 | collector | success | 5.6h fa |
| 🟡 | coppie | in_progress | 0.1h fa |
| 🟡 | database | in_progress | 2.3h fa |
| ✅ | guardiani | in_progress | 0.1h fa |
| ✅ | heartbeat | in_progress | 0.0h fa |
| ✅ | hook | in_progress | 0.2h fa |
| ✅ | iniziatori | in_progress | 0.0h fa |
| ✅ | insieme | in_progress | 0.5h fa |
| 🔧 | ispezione | cancelled | 3.7h fa |
| 🟡 | nascite | in_progress | 2.3h fa |
| ✅ | popolazione | in_progress | 0.1h fa |
| ✅ | previsioni | in_progress | 0.1h fa |
| ✅ | pulizia_riserve | success | 80.6h fa |
| ✅ | repo_gc | success | 20.7h fa |
| ✅ | riparazione | in_progress | 0.1h fa |
| 🟡 | riserve | in_progress | 0.1h fa |
| ✅ | scoperta | in_progress | 0.1h fa |
| 🔧 | sentinella | success | 4.3h fa |
| ✅ | storico | in_progress | 2.4h fa |
| 🟡 | vivo | in_progress | 0.5h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.