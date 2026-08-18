# ANALISI FASE-2 — 2026-08-18 23:31 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -33.9% su 134 token, win 6%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **134** | -33.9% | -24.6% | 6% | 0 | 0 | -2.8% | SI |
| 72h | **126** | -33.0% | -23.8% | 7% | 1 | 0 | +23.9% | SI |
| 168h | **108** | -30.4% | -23.8% | 8% | 4 | 0 | +66.2% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **134/40** PRONTO
- **72h: 126/40** PRONTO <- il trigger
- 168h: **108/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 81 | -27.4% | 7% | 1 | SI |
| 6-24h | 41 | -7.0% | 12% | 1 | SI |
| 1-3g | 41 | -36.0% | 5% | 0 | SI |
| 3-7g | 40 | -1.5% | 15% | 1 | SI |
| >7g | 48 | -20.3% | 10% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 78 | -27.4% | 5% | 1 | SI |
| 6-24h | 40 | -7.6% | 25% | 0 | SI |
| 1-3g | 35 | -12.3% | 11% | 1 | no |
| 3-7g | 40 | +55.5% | 25% | 1 | SI |
| >7g | 44 | -15.6% | 14% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 76 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 3621 wallet con <4 acquisti: piu' whale per giudicarli