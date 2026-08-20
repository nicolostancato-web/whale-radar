# ANALISI FASE-2 — 2026-08-20 01:47 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -35.4% su 142 token, win 5%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **142** | -35.4% | -25.5% | 5% | 0 | 0 | -4.3% | SI |
| 72h | **128** | -34.7% | -27.8% | 6% | 1 | 0 | +23.1% | SI |
| 168h | **118** | -36.3% | -32.3% | 8% | 3 | 0 | +49.9% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **142/40** PRONTO
- **72h: 128/40** PRONTO <- il trigger
- 168h: **118/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 86 | -29.4% | 7% | 1 | SI |
| 6-24h | 42 | -8.1% | 12% | 1 | SI |
| 1-3g | 43 | -36.8% | 5% | 0 | SI |
| 3-7g | 42 | -3.0% | 14% | 1 | SI |
| >7g | 52 | -21.0% | 10% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 76 | -28.3% | 5% | 1 | SI |
| 6-24h | 42 | -10.9% | 24% | 0 | SI |
| 1-3g | 38 | -14.6% | 10% | 1 | no |
| 3-7g | 40 | +54.2% | 25% | 1 | SI |
| >7g | 49 | -18.5% | 12% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 78 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 4210 wallet con <4 acquisti: piu' whale per giudicarli