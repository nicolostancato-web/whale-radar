# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 15 workflow attivi*

## 🔴 2 PROBLEMI
- **nascite**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **vivo**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 1 AUTO-FIXATI
- repo_gc #14: chiuso, era appeso da 145.2h e bloccava la corsia

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | success | 0.5h fa |
| ✅ | censimento | success | 0.4h fa |
| ✅ | collector | success | 0.5h fa |
| ✅ | coppie | in_progress | 0.1h fa |
| ✅ | database | pending | 0.5h fa |
| ✅ | heartbeat | success | 0.5h fa |
| ✅ | insider | success | 0.5h fa |
| ✅ | ispezione | success | 0.5h fa |
| 🟡 | nascite | in_progress | 1.1h fa |
| ✅ | repo_gc | success | 1.1h fa |
| ✅ | solana_helius | success | 0.8h fa |
| ✅ | storico | in_progress | 0.5h fa |
| ✅ | strategy_optimizer_solana | success | 497.7h fa |
| 🟡 | vivo | in_progress | 0.2h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.