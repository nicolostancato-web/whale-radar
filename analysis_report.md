# ANALISI FASE-2 — 2026-08-19 05:39 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -33.8% su 139 token, win 6%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **139** | -33.8% | -24.0% | 6% | 0 | 0 | -4.7% | SI |
| 72h | **128** | -33.9% | -25.2% | 7% | 1 | 0 | +25.1% | SI |
| 168h | **109** | -31.9% | -23.7% | 8% | 4 | 0 | +53.9% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **139/40** PRONTO
- **72h: 128/40** PRONTO <- il trigger
- 168h: **109/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 84 | -27.0% | 7% | 1 | SI |
| 6-24h | 42 | -8.0% | 12% | 1 | SI |
| 1-3g | 41 | -36.0% | 5% | 0 | SI |
| 3-7g | 42 | -3.2% | 14% | 1 | SI |
| >7g | 48 | -20.7% | 10% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 79 | -28.2% | 5% | 1 | SI |
| 6-24h | 41 | -8.7% | 24% | 0 | SI |
| 1-3g | 35 | -12.3% | 11% | 1 | no |
| 3-7g | 40 | +55.4% | 25% | 1 | SI |
| >7g | 44 | -16.2% | 14% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 78 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 3826 wallet con <4 acquisti: piu' whale per giudicarli