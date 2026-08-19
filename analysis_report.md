# ANALISI FASE-2 — 2026-08-19 19:34 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -34.2% su 141 token, win 6%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **141** | -34.2% | -23.5% | 6% | 0 | 0 | -4.0% | SI |
| 72h | **128** | -34.1% | -26.7% | 6% | 1 | 0 | +24.2% | SI |
| 168h | **113** | -35.0% | -28.9% | 8% | 4 | 0 | +52.0% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **141/40** PRONTO
- **72h: 128/40** PRONTO <- il trigger
- 168h: **113/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 85 | -27.5% | 7% | 1 | SI |
| 6-24h | 42 | -8.1% | 12% | 1 | SI |
| 1-3g | 43 | -36.8% | 5% | 0 | SI |
| 3-7g | 42 | -3.4% | 14% | 1 | SI |
| >7g | 52 | -20.8% | 12% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 76 | -28.3% | 5% | 1 | SI |
| 6-24h | 42 | -10.9% | 24% | 0 | SI |
| 1-3g | 38 | -14.6% | 10% | 1 | no |
| 3-7g | 40 | +54.2% | 25% | 1 | SI |
| >7g | 48 | -15.4% | 15% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 77 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 4140 wallet con <4 acquisti: piu' whale per giudicarli