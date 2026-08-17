# ANALISI FASE-2 — 2026-08-17 15:34 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -34.7% su 124 token, win 3%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **124** | -34.7% | -25.5% | 3% | 0 | 0 | -4.5% | SI |
| 72h | **116** | -34.1% | -25.4% | 7% | 2 | 0 | +22.0% | SI |
| 168h | **97** | -18.2% | -19.5% | 11% | 2 | 1 | +49.5% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **124/40** PRONTO
- **72h: 116/40** PRONTO <- il trigger
- 168h: **97/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 77 | -34.9% | 5% | 0 | SI |
| 6-24h | 39 | -12.0% | 10% | 1 | no |
| 1-3g | 34 | -35.3% | 6% | 0 | no |
| 3-7g | 39 | -1.8% | 13% | 1 | no |
| >7g | 40 | -18.9% | 8% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 71 | -34.4% | 4% | 0 | SI |
| 6-24h | 37 | -8.0% | 24% | 0 | no |
| 1-3g | 33 | -12.5% | 9% | 1 | no |
| 3-7g | 34 | +72.0% | 26% | 1 | no |
| >7g | 39 | -16.4% | 13% | 0 | no |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 63 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 3382 wallet con <4 acquisti: piu' whale per giudicarli