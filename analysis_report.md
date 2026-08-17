# ANALISI FASE-2 — 2026-08-17 21:34 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -35.1% su 126 token, win 4%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **126** | -35.1% | -26.1% | 4% | 0 | 0 | -2.6% | SI |
| 72h | **118** | -33.2% | -24.4% | 8% | 2 | 0 | +25.8% | SI |
| 168h | **99** | -15.9% | -19.9% | 11% | 3 | 1 | +71.8% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **126/40** PRONTO
- **72h: 118/40** PRONTO <- il trigger
- 168h: **99/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 78 | -28.1% | 6% | 1 | SI |
| 6-24h | 41 | -7.0% | 12% | 1 | SI |
| 1-3g | 36 | -34.8% | 6% | 0 | no |
| 3-7g | 40 | -1.1% | 15% | 1 | SI |
| >7g | 41 | -19.1% | 7% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 72 | -27.7% | 6% | 1 | SI |
| 6-24h | 38 | -4.2% | 26% | 0 | no |
| 1-3g | 35 | -12.0% | 11% | 1 | no |
| 3-7g | 36 | +71.0% | 28% | 1 | no |
| >7g | 40 | -16.9% | 12% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 64 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 3483 wallet con <4 acquisti: piu' whale per giudicarli