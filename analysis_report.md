# ANALISI FASE-2 — 2026-08-18 16:43 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -34.7% su 129 token, win 5%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **129** | -34.7% | -24.0% | 5% | 0 | 0 | -2.6% | SI |
| 72h | **121** | -32.5% | -23.4% | 8% | 2 | 0 | +25.1% | SI |
| 168h | **107** | -19.3% | -23.7% | 9% | 4 | 1 | +69.6% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **129/40** PRONTO
- **72h: 121/40** PRONTO <- il trigger
- 168h: **107/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 79 | -28.0% | 6% | 1 | SI |
| 6-24h | 41 | -7.0% | 12% | 1 | SI |
| 1-3g | 38 | -35.9% | 5% | 0 | no |
| 3-7g | 40 | -1.4% | 15% | 1 | SI |
| >7g | 46 | -19.9% | 9% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 74 | -27.8% | 5% | 1 | SI |
| 6-24h | 39 | -5.6% | 26% | 0 | no |
| 1-3g | 35 | -12.3% | 11% | 1 | no |
| 3-7g | 38 | +61.9% | 26% | 1 | no |
| >7g | 43 | -17.1% | 12% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 70 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 3525 wallet con <4 acquisti: piu' whale per giudicarli