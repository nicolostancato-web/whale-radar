# ANALISI FASE-2 — 2026-08-27 09:30 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -34.4% su 239 token, win 3%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **239** | -34.4% | -23.2% | 3% | 0 | 0 | -9.5% | SI |
| 72h | **253** | -35.5% | -26.2% | 5% | 2 | 0 | +7.1% | SI |
| 168h | **232** | -33.9% | -26.8% | 11% | 4 | 0 | +20.4% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **239/40** PRONTO
- **72h: 253/40** PRONTO <- il trigger
- 168h: **232/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 109 | -33.6% | 6% | 1 | SI |
| 6-24h | 62 | -16.7% | 14% | 1 | SI |
| 1-3g | 63 | -32.4% | 5% | 0 | SI |
| 3-7g | 67 | -14.9% | 10% | 1 | SI |
| >7g | 94 | -25.3% | 3% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 102 | -37.6% | 4% | 1 | SI |
| 6-24h | 58 | -17.3% | 21% | 0 | SI |
| 1-3g | 66 | -23.6% | 8% | 1 | SI |
| 3-7g | 72 | +15.8% | 17% | 1 | SI |
| >7g | 108 | -27.1% | 6% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 210 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 7572 wallet con <4 acquisti: piu' whale per giudicarli