# ANALISI FASE-2 — 2026-08-18 03:55 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -35.0% su 127 token, win 5%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **127** | -35.0% | -26.5% | 5% | 0 | 0 | -2.5% | SI |
| 72h | **119** | -32.6% | -25.1% | 8% | 2 | 0 | +25.7% | SI |
| 168h | **102** | -15.4% | -20.1% | 12% | 4 | 1 | +71.3% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **127/40** PRONTO
- **72h: 119/40** PRONTO <- il trigger
- 168h: **102/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 78 | -28.1% | 6% | 1 | SI |
| 6-24h | 41 | -7.0% | 12% | 1 | SI |
| 1-3g | 38 | -35.9% | 5% | 0 | no |
| 3-7g | 40 | -1.3% | 15% | 1 | SI |
| >7g | 43 | -19.4% | 9% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 73 | -27.7% | 6% | 1 | SI |
| 6-24h | 38 | -4.2% | 26% | 0 | no |
| 1-3g | 35 | -12.0% | 11% | 1 | no |
| 3-7g | 37 | +66.4% | 27% | 1 | no |
| >7g | 41 | -16.1% | 12% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 68 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 3503 wallet con <4 acquisti: piu' whale per giudicarli