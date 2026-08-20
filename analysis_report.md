# ANALISI FASE-2 — 2026-08-20 14:49 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -35.1% su 151 token, win 5%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **151** | -35.1% | -25.3% | 5% | 0 | 0 | -4.3% | SI |
| 72h | **137** | -34.0% | -24.7% | 5% | 1 | 0 | +22.9% | SI |
| 168h | **119** | -32.4% | -30.8% | 9% | 4 | 0 | +49.4% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **151/40** PRONTO
- **72h: 137/40** PRONTO <- il trigger
- 168h: **119/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 89 | -30.2% | 7% | 1 | SI |
| 6-24h | 42 | -8.1% | 12% | 1 | SI |
| 1-3g | 43 | -36.8% | 5% | 0 | SI |
| 3-7g | 42 | -3.0% | 14% | 1 | SI |
| >7g | 58 | -20.8% | 10% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 77 | -28.1% | 5% | 1 | SI |
| 6-24h | 42 | -10.9% | 24% | 0 | SI |
| 1-3g | 40 | -17.9% | 10% | 1 | SI |
| 3-7g | 41 | +52.2% | 24% | 1 | SI |
| >7g | 56 | -18.6% | 11% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 91 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 4290 wallet con <4 acquisti: piu' whale per giudicarli