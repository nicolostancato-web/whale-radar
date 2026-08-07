# 🔬 EXPERIMENTS — registro esperimenti (per non rifarli)
> Aggiorno DOPO ogni analisi. Max 2 frasi per campo.

| Data | Obiettivo | Metodo | Risultato | Conclusione |
|---|---|---|---|---|
| 2026-08-06 | Edge whale-copy Solana? | causal replay + forward study 39k eventi | media forward NEGATIVA a ogni latenza; wallet reali = wash | **Nessun edge. Strategia chiusa.** |
| 2026-08-07 | Edge grandi-acquisti Robinhood? | backtest 607 eventi, scale-out, net fee+slippage | portafoglio +8-13% (size piccola) | **Aspettativa POSITIVA** |
| 2026-08-07 | È overfit? | walk-forward (train 60% / test 40% OOS) | train +7,8% / **test +13,2%** | **NON overfit** (regge out-of-sample) |
| 2026-08-07 | È un numero magico? | sensibilità soglia spike 3x-8x | tutti positivi (+9,9% a +15,2%) | **Robusto** (non fragile) |
| 2026-08-07 | Il filtro "whale vera" aiuta? | spike con volume >= $15k vs tutti | identico | **No → è momentum, non smart-money** |
| 2026-08-07 | Regge dal vivo? | paper test live out-of-sample | **in corso** (chiude survivorship) | da valutare in 1-2 settimane |

## ⚠️ Buco noto aperto
**Survivorship:** i dati storici hanno solo i token vivi oggi. Lo chiude solo il paper test live (in avanti include i token che moriranno).
