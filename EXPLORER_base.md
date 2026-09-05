# 🔬 EXPLORER — LOOP 1: come alzo la percentuale? (base)
*2026-09-05 07:09 UTC · 158 strategie provate in questo ciclo · 64577 in totale*

## Migliore trovata finora: **-8%** (stress test) · P&L medio **+6%** · crescita composta **-13.6%** · 5% peggiore **-84%** · 171 trade

*La percentuale grande è lo STRESS TEST (tolto il 5% migliore): serve a non farsi ingannare
dai colpi fortunati, ma non è il rendimento atteso. Il P&L medio è quello che il conto vedrebbe;
la crescita composta dice se reinvestendo si cresce o ci si rovina.*

*Il punteggio è il **minimo** fra la robusta su tutto lo storico (-8%) e quella sui token più RECENTI (-3%): cerchiamo qualcosa che funzioni domani, non che abbia funzionato un mese fa.*

**La strategia:** entra +6h · solo se volume > $10.000, almeno 2h di scambi · stop -60% · profitto a 4x e 8x · trailing -50% · soglia 0.4
**I segnali guardati:** `dump_depth, log_vol, log_vol_accel, frac_verdi, log_buyusd`

- migliorie trovate in questo ciclo: **0**
- il cancello del LIVE si apre a **+40%** robusta → oggi 🔴 chiuso (mancano 48 punti)

## Le strategie che hanno alzato la percentuale

| quando | da | a | vinti | la strategia |
|---|---|---|---|---|
| 31/08 08:31 | +16% | **+21%** | 21% | entra +2h · stop -70% · profitto a 5x e 15x · trailing -30% · soglia 0.4 |
| 31/08 08:01 | +8% | **+16%** | 21% | entra +2h · stop -70% · prende profitto a 5x e 15x · lascia correre col trailing -50% · soglia di ingresso 0.4 |
| 31/08 08:01 | +1% | **+8%** | 22% | entra +2h · stop -70% · prende profitto a 3x e 15x · lascia correre col trailing -50% · soglia di ingresso 0.4 |
| 31/08 08:01 | -4% | **+1%** | 21% | entra +2h · stop -70% · prende profitto a 3x e 6x · lascia correre col trailing -50% · soglia di ingresso 0.4 |

## Le ultime provate e scartate

| la strategia | risultato |
|---|---|
| entra +6h · solo se volume > $3.000, almeno 2h di scambi · stop -60% · profitto a 4x e 8x · trailing -50% · soglia 0.4 | -13% |
| entra +6h · solo se volume > $10.000, almeno 2h di scambi · stop -60% · profitto a 4x e 8x · trailing -50% · soglia 0.3 | -11% |
| entra +6h · solo se volume > $10.000, almeno 2h di scambi · stop -60% · profitto a 4x e 8x · trailing -50% · soglia 0.35 | -10% |
| entra +6h · solo se volume > $10.000, almeno 2h di scambi · stop -60% · profitto a 4x e 8x · trailing -50% · soglia 0.4 | -8% |
| entra +6h · solo se volume > $10.000, almeno 2h di scambi · stop -60% · profitto a 4x e 8x · trailing -50% · soglia 0.4 | -8% |
| entra +6h · solo se volume > $3.000, almeno 2h di scambi · stop -60% · profitto a 4x e 8x · trailing -50% · soglia 0.4 | -13% |

> Il LOOP 1 non si ferma mai: prova strategie e segnali, tiene solo cio' che alza la percentuale
> ROBUSTA (tolti i 3 colpi migliori) di almeno 8 punti, e riparte da li'.
> **Propone, non applica**: cambiare la strategia viva e' una decisione umana (DECISIONS.md).