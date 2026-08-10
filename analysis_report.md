# ANALISI FASE-2 — 2026-08-10 17:56 UTC

**Verdetto: DATI INSUFFICIENTI** — campione troppo poco diverso (24h su 31 token, servono 40+). Nessun numero e' affidabile.

## Risultati per finestra (netti di slippage, survivorship-corretti)
| Finestra | n_trade | **n_token** | netto medio | mediana | %win | 2x+ | 5x+ | morti | affidabile? |
|---|---|---|---|---|---|---|---|---|---|
| 24h | 846 | **31** | -13.9% | -5.6% | 43% | 1 | 0 | 0 | NO (aneddoto) |
| 72h | 231 | **1** | +24.0% | +11.8% | 98% | 0 | 0 | 0 | NO (aneddoto) |
| 168h | 0 | 0 | - | - | - | - | - | - | NO |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 46 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[HIGH]** finestra 24h misurabile su solo 31 token diversi (<40): serve tempo+piu' token
- **[MEDIUM]** finestra 72h misurabile su solo 1 token diversi (<40): serve tempo+piu' token
- **[MEDIUM]** finestra 168h misurabile su solo 0 token diversi (<40): serve tempo+piu' token
- **[MEDIUM]** 303 wallet con <4 acquisti: piu' whale per giudicarli