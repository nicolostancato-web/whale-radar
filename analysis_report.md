# ANALISI FASE-2 — 2026-08-21 17:38 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -33.6% su 170 token, win 5%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **170** | -33.6% | -21.8% | 5% | 0 | 0 | -4.0% | SI |
| 72h | **161** | -34.8% | -24.3% | 5% | 2 | 0 | +22.2% | SI |
| 168h | **120** | -33.3% | -31.9% | 9% | 4 | 0 | +43.8% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **170/40** PRONTO
- **72h: 161/40** PRONTO <- il trigger
- 168h: **120/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 93 | -30.2% | 8% | 1 | SI |
| 6-24h | 49 | -11.7% | 12% | 1 | SI |
| 1-3g | 47 | -35.6% | 4% | 0 | SI |
| 3-7g | 45 | -3.5% | 13% | 1 | SI |
| >7g | 64 | -20.7% | 9% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 82 | -32.2% | 5% | 1 | SI |
| 6-24h | 45 | -13.2% | 22% | 0 | SI |
| 1-3g | 47 | -21.4% | 8% | 1 | SI |
| 3-7g | 45 | +46.3% | 22% | 1 | SI |
| >7g | 65 | -16.9% | 9% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 111 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 4802 wallet con <4 acquisti: piu' whale per giudicarli