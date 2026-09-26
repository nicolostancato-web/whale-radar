# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 25 workflow attivi*

## 🔴 8 PROBLEMI
- **censimento**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **database**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **insieme**: 3 run FALLITE nelle ultime 6 (bug reale, da guardare)
- **nascite**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **previsioni**: 2 run FALLITE nelle ultime 6 (bug reale, da guardare)
- **riserve**: 2 run FALLITE nelle ultime 6 (bug reale, da guardare)
- **storico**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **vivo**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 3 AUTO-FIXATI
- **collector**: fermo da 6.0h → RI-LANCIATO ✅
- **ispezione**: fermo da 4.1h → RI-LANCIATO ✅
- **sentinella**: fermo da 5.0h → RI-LANCIATO ✅

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| 🔴 | insieme | success | 0.9h fa |
| 🔴 | previsioni | in_progress | 0.3h fa |
| 🔴 | riserve | in_progress | 0.1h fa |
| ✅ | accumulator | in_progress | 0.0h fa |
| ✅ | assottiglia | success | 74.4h fa |
| 🟡 | censimento | in_progress | 0.0h fa |
| 🔧 | collector | success | 6.0h fa |
| ✅ | coppie | pending | 0.0h fa |
| 🟡 | database | pending | 1.3h fa |
| ✅ | guardiani | success | 0.1h fa |
| ✅ | heartbeat | in_progress | 0.0h fa |
| ✅ | hook | in_progress | 0.1h fa |
| ✅ | iniziatori | in_progress | 0.1h fa |
| 🔧 | ispezione | cancelled | 4.1h fa |
| 🟡 | nascite | in_progress | 0.5h fa |
| ✅ | popolazione | pending | 0.0h fa |
| ✅ | pubblicatore | success | 1.0h fa |
| ✅ | pulizia_riserve | success | 87.0h fa |
| ✅ | repo_gc | success | 3.3h fa |
| ✅ | riparazione | in_progress | 0.1h fa |
| ✅ | scoperta | in_progress | 0.1h fa |
| 🔧 | sentinella | success | 5.0h fa |
| 🟡 | storico | pending | 0.1h fa |
| 🟡 | vivo | in_progress | 0.2h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.