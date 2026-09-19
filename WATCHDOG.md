# 🛡️ WORKFLOW WATCHDOG — guardiano dei reparti
*controllo ogni 2h · 16 workflow attivi*

## 🔴 2 PROBLEMI
- **nascite**: 4 cancellazioni (sovrapposizioni? controllare frequenza cron)
- **vivo**: 3 cancellazioni (sovrapposizioni? controllare frequenza cron)

## 🔧 3 AUTO-FIXATI
- **censimento**: fermo da 2.8h → RI-LANCIATO ✅
- repo_gc #14: chiuso, era appeso da 147.6h e bloccava la corsia
- **solana_helius**: fermo da 3.2h → RI-LANCIATO ✅

## Stato per workflow
| | workflow | ultima run | età |
|---|---|---|---|
| ✅ | accumulator | in_progress | 0.0h fa |
| 🔧 | censimento | success | 2.8h fa |
| ✅ | collector | success | 1.0h fa |
| ✅ | coppie | in_progress | 0.1h fa |
| ✅ | database | pending | 2.9h fa |
| ✅ | heartbeat | in_progress | 0.0h fa |
| ✅ | insider | success | 2.9h fa |
| ✅ | ispezione | success | 1.8h fa |
| 🟡 | nascite | in_progress | 0.9h fa |
| ✅ | popolazione | in_progress | 0.1h fa |
| ✅ | repo_gc | success | 3.5h fa |
| 🔧 | solana_helius | success | 3.2h fa |
| ✅ | storico | in_progress | 0.1h fa |
| ✅ | strategy_optimizer_solana | success | 500.1h fa |
| 🟡 | vivo | in_progress | 0.7h fa |
| ✅ | workflow_watchdog | in_progress | 0.0h fa |

> Se qui c'e' 🔴/🟠, il problema e' gia' noto e (dove possibile) gia' ri-lanciato — non serve che lo scopra Nicolo con 'news?'.