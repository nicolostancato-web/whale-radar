# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 31 workflow attivi*

## 🔴 15 PROBLEMI
- **astra**: 3 run FALLITE nelle ultime 6 (bug reale, da guardare)
- **censimento**: 6 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **coppie**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **database**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **heartbeat**: 6 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **hook**: 6 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **iniziatori**: 6 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **nascite**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **piu_intelligente**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **previsioni**: 6 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **riparazione**: 6 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **riserve**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **scoperta**: 6 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **storico**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **vivo**: 5 cancellazioni (sovrapposizioni? controllare frequenza cron)

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| 🔴 | astra | failure | 1.4h fa |
| ✅ | accumulator | in_progress | 0.0h fa |
| 🟡 | censimento | cancelled | 1.4h fa |
| ✅ | collector | success | 1.4h fa |
| 🟡 | coppie | in_progress | 0.4h fa |
| 🟡 | database | in_progress | 1.0h fa |
| ✅ | deposito | success | 0.3h fa |
| ✅ | guardiani | success | 1.4h fa |
| 🟡 | heartbeat | cancelled | 1.5h fa |
| 🟡 | hook | cancelled | 1.4h fa |
| 🟡 | iniziatori | cancelled | 1.4h fa |
| ✅ | insieme | in_progress | 0.1h fa |
| ✅ | ispezione | success | 1.0h fa |
| 🟡 | nascite | in_progress | 0.5h fa |
| 🟡 | piu_intelligente | cancelled | 12.6h fa |
| ✅ | popolazione | in_progress | 0.0h fa |
| 🟡 | previsioni | cancelled | 1.4h fa |
| ✅ | prova_avanti | in_progress | 1.4h fa |
| ✅ | pubblicatore | success | 1.5h fa |
| ✅ | repo_gc | success | 14.7h fa |
| 🟡 | riparazione | cancelled | 1.4h fa |
| 🟡 | riserve | in_progress | 1.4h fa |
| 🟡 | scoperta | cancelled | 1.4h fa |
| ✅ | sentinella | success | 1.4h fa |
| ✅ | soccorso | success | 1.5h fa |
| 🟡 | storico | pending | 0.1h fa |
| 🟡 | vivo | in_progress | 1.1h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.