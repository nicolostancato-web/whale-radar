# ANALISI FASE-2 — 2026-08-20 21:37 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -34.0% su 156 token, win 6%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **156** | -34.0% | -22.1% | 6% | 0 | 0 | -4.3% | SI |
| 72h | **141** | -32.9% | -23.6% | 6% | 2 | 0 | +22.8% | SI |
| 168h | **120** | -32.8% | -31.4% | 9% | 4 | 0 | +50.0% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **156/40** PRONTO
- **72h: 141/40** PRONTO <- il trigger
- 168h: **120/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 91 | -30.5% | 7% | 1 | SI |
| 6-24h | 44 | -7.9% | 14% | 1 | SI |
| 1-3g | 42 | -33.0% | 7% | 0 | SI |
| 3-7g | 43 | -3.4% | 14% | 1 | SI |
| >7g | 60 | -19.6% | 12% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 78 | -28.8% | 5% | 1 | SI |
| 6-24h | 43 | -11.0% | 23% | 0 | SI |
| 1-3g | 39 | -17.8% | 10% | 1 | no |
| 3-7g | 42 | +50.5% | 24% | 1 | SI |
| >7g | 60 | -15.4% | 12% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 97 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 4522 wallet con <4 acquisti: piu' whale per giudicarli