# ANALISI FASE-2 — 2026-08-21 04:49 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -33.4% su 159 token, win 5%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **159** | -33.4% | -22.1% | 5% | 0 | 0 | -4.6% | SI |
| 72h | **148** | -33.6% | -24.0% | 5% | 2 | 0 | +22.3% | SI |
| 168h | **122** | -32.5% | -30.1% | 9% | 4 | 0 | +49.3% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **159/40** PRONTO
- **72h: 148/40** PRONTO <- il trigger
- 168h: **122/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 92 | -29.8% | 8% | 1 | SI |
| 6-24h | 45 | -7.9% | 13% | 1 | SI |
| 1-3g | 42 | -36.3% | 5% | 0 | SI |
| 3-7g | 45 | -3.8% | 13% | 1 | SI |
| >7g | 60 | -20.1% | 10% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 81 | -30.6% | 5% | 1 | SI |
| 6-24h | 43 | -11.0% | 23% | 0 | SI |
| 1-3g | 41 | -19.1% | 10% | 1 | SI |
| 3-7g | 45 | +45.8% | 22% | 1 | SI |
| >7g | 60 | -15.2% | 12% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 100 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 4560 wallet con <4 acquisti: piu' whale per giudicarli