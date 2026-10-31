# L'età di chi compra: non è il portafoglio nuovo

*2 ottobre 2026 · 19.858 pool su robinhood e 5.034 su base (86% e 85% dei giudicabili)*

## Il dato, e il fatto che era gratis

Ogni transazione porta il suo **nonce**: quante transazioni quel portafoglio aveva **mai** fatto
prima di firmare quella. Arrivava dentro la stessa risposta che chiediamo dal 25/09 per sapere
chi ha firmato, e per sei giorni l'abbiamo **scartata**. Costo per recuperarla: **zero chiamate**.

## Chi compra per primo non è una persona nuova: è una macchina

| | robinhood | base |
|---|---|---|
| nonce mediano del primo compratore | **4.023** | **9.753** |
| nonce massimo visto | 3.582.429 | **16.255.643** |
| con nonce ≤ 1 (portafoglio nato ora) | 2,6% | 4,0% |
| con nonce ≤ 10 | 5,8% | 10,6% |

Il compratore tipico di una moneta appena nata ha già fatto **migliaia** di transazioni. Il
portafoglio appena creato — l'insider col wallet nuovo — è il **2,6-4,0%** dei casi.

## E l'età non predice l'esito

| il compratore più nuovo aveva fatto | robinhood | base |
|---|---|---|
| 2-10 transazioni | −15,7% | — |
| 11-100 | −15,0% | **−58,0%** |
| 101-1.000 | −9,2% | −42,9% |
| 1.001-10.000 | **−5,7%** | −45,4% |
| oltre 10.000 | −14,1% | **−29,8%** |

**Non monotona, e le chain vanno in direzioni opposte**: su robinhood il migliore sta in mezzo,
su base più il portafoglio è vecchio meglio va. Nessuna casella positiva. La regola di
ripetizione boccia.

## Cosa NON si può ancora dire

La casella che interessa — **nonce 0-1**, il portafoglio nato per quella moneta — ha meno di
quaranta pool: **non è misurabile**, non è negativa. Dire «i portafogli nuovi non funzionano»
sarebbe esattamente l'errore del 22/09, dedurre un fatto del mondo da un limite nostro.

Si apre con la copertura: oggi il nonce è noto per 17.000 transazioni su 674.914 (2,5%), e sta
salendo a ogni giro.

## Dove resta l'ipotesi insider

Due versioni provate e cadute: le **squadre visibili** (vanno peggio, −19,8% su robinhood) e i
**portafogli nuovi** (non predicono). Quella che regge è il **passato chiuso del singolo
portafoglio**: 16-20 punti, su entrambe le chain, sopravvissuto a due attacchi.

Quella mai provata è la più forte: **chi finanzia**. E qui c'è un ostacolo reale e misurato —
un RPC pubblico **non sa elencare le transazioni di un indirizzo**: `eth_getLogs` su tutta la
storia risponde «query spans 78.134.721 blocks», e il finanziamento in valuta nativa non lascia
log. Serve un indicizzatore (a pagamento) oppure scandire i blocchi (gratis ma molte chiamate).
Prima di proporre una spesa va misurato quanto costa la strada gratis: è il prossimo passo.
