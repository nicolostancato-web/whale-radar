# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 15 workflow attivi*

## 🔴 3 PROBLEMI
- **database**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **nascite**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **vivo**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 2 AUTO-FIXATI
- **ispezione**: fermo da 3.0h → RI-LANCIATO ✅
- repo_gc #14: chiuso, era appeso da 152.4h e bloccava la corsia

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | in_progress | 0.0h fa |
| ✅ | censimento | success | 0.5h fa |
| ✅ | collector | success | 1.2h fa |
| ✅ | coppie | in_progress | 0.1h fa |
| 🟡 | database | pending | 3.3h fa |
| ✅ | heartbeat | in_progress | 0.0h fa |
| ✅ | insider | success | 7.7h fa |
| 🔧 | ispezione | success | 3.0h fa |
| 🟡 | nascite | pending | 1.4h fa |
| ✅ | popolazione | in_progress | 0.7h fa |
| ✅ | repo_gc | success | 8.3h fa |
| ✅ | solana_helius | success | 0.6h fa |
| ✅ | storico | success | 4.9h fa |
| 🟡 | vivo | in_progress | 0.8h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.