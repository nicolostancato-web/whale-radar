# ANALISI FASE-2 — 2026-08-21 11:35 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -33.6% su 163 token, win 5%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **163** | -33.6% | -22.0% | 5% | 0 | 0 | -3.7% | SI |
| 72h | **152** | -33.8% | -23.8% | 5% | 2 | 0 | +22.9% | SI |
| 168h | **120** | -33.3% | -32.1% | 9% | 4 | 0 | +44.4% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **163/40** PRONTO
- **72h: 152/40** PRONTO <- il trigger
- 168h: **120/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 92 | -30.4% | 8% | 1 | SI |
| 6-24h | 46 | -8.2% | 13% | 1 | SI |
| 1-3g | 45 | -36.3% | 4% | 0 | SI |
| 3-7g | 45 | -3.5% | 13% | 1 | SI |
| >7g | 62 | -20.1% | 10% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 80 | -31.1% | 5% | 1 | SI |
| 6-24h | 43 | -11.0% | 23% | 0 | SI |
| 1-3g | 44 | -19.9% | 9% | 1 | SI |
| 3-7g | 45 | +46.1% | 22% | 1 | SI |
| >7g | 63 | -15.4% | 11% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 105 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 4741 wallet con <4 acquisti: piu' whale per giudicarli