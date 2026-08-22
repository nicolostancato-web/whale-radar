# ANALISI FASE-2 — 2026-08-22 08:41 UTC

**Verdetto: NESSUN EDGE** — rendimento netto medio 24h -33.2% su 179 token, win 4%

## Risultati per finestra (EQUAL-WEIGHT PER TOKEN, netti di slippage, survivorship-corretti)
| Finestra | **n_token** | netto medio/token | mediana | %token positivi | 2x+ | 5x+ | (per-trade) | affidabile? |
|---|---|---|---|---|---|---|---|---|
| 24h | **179** | -33.2% | -20.9% | 4% | 0 | 0 | -5.4% | SI |
| 72h | **171** | -34.6% | -23.1% | 5% | 2 | 0 | +17.1% | SI |
| 168h | **139** | -32.7% | -20.9% | 8% | 4 | 0 | +35.4% | SI |

> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto 40 token = aneddoto, non fidarsi.

## 🎯 TRIGGER FASE 2 (analisi multi-giorno affidabile)
La tesi 'tieni per giorni -> 5x' si giudica sul 72h/168h. Serve 40+ token diversi per finestra.
- 24h: **179/40** PRONTO
- **72h: 171/40** PRONTO <- il trigger
- 168h: **139/40** PRONTO
- **STATO: ✅ FASE 2 PRONTA — verdetto multi-giorno affidabile**

## Per ETA' del token all'ingresso della balena — finestra 24h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 97 | -30.3% | 7% | 1 | SI |
| 6-24h | 49 | -12.3% | 12% | 1 | SI |
| 1-3g | 49 | -35.0% | 4% | 0 | SI |
| 3-7g | 47 | -5.5% | 13% | 1 | SI |
| >7g | 69 | -21.6% | 7% | 0 | SI |

## Per ETA' del token all'ingresso della balena — finestra 72h
| eta' token | n_token | netto medio/token | %token positivi | 5x+ | affidabile? |
|---|---|---|---|---|---|
| <6h | 85 | -32.8% | 5% | 1 | SI |
| 6-24h | 48 | -15.2% | 21% | 0 | SI |
| 1-3g | 50 | -21.1% | 8% | 1 | SI |
| 3-7g | 45 | +46.4% | 22% | 1 | SI |
| >7g | 68 | -17.0% | 10% | 0 | SI |

> Se una fascia d'eta' spicca (netto positivo su 40+ token), quello e' il candidato edge da simulare.

## Gap di dati rilevati (ordini per la Fase 1)
- **[HIGH]** 123 token con balena hanno <72 candele orarie -> scaricare piu' candele
- **[MEDIUM]** 5090 wallet con <4 acquisti: piu' whale per giudicarli