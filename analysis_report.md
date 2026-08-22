# ANALISI FASE-2 — 2026-08-22 01:45 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -33.3% su 173 token, win 5%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **173** | -33.3% | -21.6% | 5% | 0 | 0 | -5.0% | SI |
| 72h | **165** | -34.7% | -23.7% | 5% | 2 | 0 | +18.8% | SI |
| 168h | **133** | -32.0% | -21.9% | 8% | 4 | 0 | +38.9% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **173/40** PRONTO
- **72h: 165/40** PRONTO <- il trigger
- 168h: **133/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 95 | -29.8% | 7% | 1 | SI |
| 6-24h | 50 | -12.3% | 12% | 1 | SI |
| 1-3g | 47 | -35.7% | 4% | 0 | SI |
| 3-7g | 47 | -5.5% | 13% | 1 | SI |
| >7g | 66 | -21.3% | 9% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 84 | -32.1% | 5% | 1 | SI |
| 6-24h | 47 | -14.9% | 21% | 0 | SI |
| 1-3g | 47 | -21.3% | 8% | 1 | SI |
| 3-7g | 45 | +46.4% | 22% | 1 | SI |
| >7g | 66 | -16.5% | 11% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 115 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 4931 wallet con <4 acquisti: piu' whale per giudicarli