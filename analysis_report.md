# ANALISI FASE-2 — 2026-08-22 15:30 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -34.0% su 182 token, win 3%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **182** | -34.0% | -21.9% | 3% | 0 | 0 | -5.5% | SI |
| 72h | **173** | -34.9% | -23.4% | 5% | 2 | 0 | +16.6% | SI |
| 168h | **144** | -33.0% | -20.6% | 8% | 4 | 0 | +35.2% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **182/40** PRONTO
- **72h: 173/40** PRONTO <- il trigger
- 168h: **144/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 98 | -31.8% | 6% | 1 | SI |
| 6-24h | 49 | -12.3% | 12% | 1 | SI |
| 1-3g | 49 | -35.0% | 4% | 0 | SI |
| 3-7g | 49 | -6.6% | 12% | 1 | SI |
| >7g | 69 | -21.6% | 6% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 86 | -33.2% | 5% | 1 | SI |
| 6-24h | 49 | -16.7% | 20% | 0 | SI |
| 1-3g | 51 | -21.6% | 8% | 1 | SI |
| 3-7g | 46 | +44.2% | 22% | 1 | SI |
| >7g | 68 | -17.5% | 9% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 122 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 5091 wallet con <4 acquisti: piu' whale per giudicarli