# ANALISI FASE-2 — 2026-08-19 13:04 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -34.0% su 141 token, win 6%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **141** | -34.0% | -23.5% | 6% | 0 | 0 | -5.1% | SI |
| 72h | **127** | -33.8% | -25.8% | 6% | 1 | 0 | +23.6% | SI |
| 168h | **110** | -33.1% | -26.4% | 8% | 4 | 0 | +51.9% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **141/40** PRONTO
- **72h: 127/40** PRONTO <- il trigger
- 168h: **110/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 85 | -27.5% | 7% | 1 | SI |
| 6-24h | 42 | -8.0% | 12% | 1 | SI |
| 1-3g | 43 | -35.9% | 5% | 0 | SI |
| 3-7g | 42 | -3.2% | 14% | 1 | SI |
| >7g | 50 | -21.2% | 10% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 78 | -28.3% | 5% | 1 | SI |
| 6-24h | 41 | -8.7% | 24% | 0 | SI |
| 1-3g | 35 | -12.4% | 11% | 1 | no |
| 3-7g | 40 | +55.4% | 25% | 1 | SI |
| >7g | 45 | -15.6% | 13% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 80 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 4001 wallet con <4 acquisti: piu' whale per giudicarli