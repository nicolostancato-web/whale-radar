# 🔬 EXPLORER — LOOP 1: come alzo la percentuale? (robinhood)
*2026-09-02 18:38 UTC · 119 strategie provate in questo ciclo · 1181 in totale*

## Migliore trovata finora: **-36%** (stress test) · P&L medio **-25%** · crescita composta **-57.9%** · 5% peggiore **-91%** · 252 trade

*La percentuale grande è lo STRESS TEST (tolto il 5% migliore): serve a non farsi ingannare
dai colpi fortunati, ma non è il rendimento atteso. Il P&L medio è quello che il conto vedrebbe;
la crescita composta dice se reinvestendo si cresce o ci si rovina.*

*Il punteggio è il **minimo** fra la robusta su tutto lo storico (-36%) e quella sui token più RECENTI (-36%): cerchiamo qualcosa che funzioni domani, non che abbia funzionato un mese fa.*

**La strategia:** entra +12h · stop -70% · profitto a 3x e 6x · trailing -50% · soglia 0.4
**I segnali guardati:** `dump_depth, log_vol, buy_pressure, volatilita, log_vol_accel, frac_verdi, sell_ratio, log_buyusd, log_nfirstbuyers, buy_accel`

- migliorie trovate in questo ciclo: **1**
- il cancello del LIVE si apre a **+40%** robusta → oggi 🔴 chiuso (mancano 76 punti)

## Le strategie che hanno alzato la percentuale

| quando | da | a | vinti | la strategia |
|---|---|---|---|---|
| 02/09 18:38 | -50% | **-36%** | 20% | entra +12h · stop -70% · profitto a 3x e 6x · trailing -50% · soglia 0.4 |

## Le ultime provate e scartate

| la strategia | risultato |
|---|---|
| entra +12h · stop -70% · profitto a 3x e 6x · trailing -50% · soglia 0.4 | -36% |
| entra +6h · stop -70% · profitto a 3x e 6x · trailing -50% · soglia 0.4 | -45% |
| entra +12h · stop -70% · profitto a 3x e 6x · trailing -50% · soglia 0.4 | -36% |
| entra +12h · stop -70% · profitto a 3x e 6x · trailing -50% · soglia 0.4 | -37% |
| entra +12h · stop -70% · profitto a 3x e 6x · trailing -50% · soglia 0.45 | -36% |
| entra +12h · stop -70% · profitto a 3x e 6x · trailing -50% · soglia 0.4 | -37% |

> Il LOOP 1 non si ferma mai: prova strategie e segnali, tiene solo cio' che alza la percentuale
> ROBUSTA (tolti i 3 colpi migliori) di almeno 8 punti, e riparte da li'.
> **Propone, non applica**: cambiare la strategia viva e' una decisione umana (DECISIONS.md).