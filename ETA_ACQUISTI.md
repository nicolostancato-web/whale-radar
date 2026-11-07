# Il 100% non arrivera' mai: meta' di quegli acquisti non esiste

*4 ottobre 2026 · risposta alla domanda di Nicolo' «quanto ci metti ad avere tutti gli acquisti?»*

## Prima dell'ETA: l'ETA esiste?

Senza il lato acquisto non si sa chi ha guadagnato, e il 42-44% delle posizioni sono «solo
vendite»: vediamo vendere gettoni che non abbiamo visto comprare. La domanda giusta non era
«quanto ci vuole» ma **«quanto di questo e' recuperabile»**.

Tre misure, prima di stimare qualunque tempo:

| | base | robinhood |
|---|---|---|
| pool con file di scambi | 84,6% | 90,2% |
| transazioni con firmatario noto | 397.820 | 723.814 |
| file di scambi riscritti in 24h | 155.000 tocchi su 136.000 file (entrambe) ||

La copertura **non e' in crescita verso il 100%: e' al suo tetto**, e i file vengono riapprofonditi
ogni giorno. Quindi il 42-44% non e' spiegato da dati non ancora raccolti.

## Il test, scritto prima di guardare

Se il primo scambio archiviato di una pool precede di almeno un'ora la prima vendita di un
portafoglio, **stavamo guardando** quando quel portafoglio ha avuto i gettoni. Se non l'abbiamo
visto comprare mentre guardavamo, non li ha comprati: **li ha ricevuti** — dal lanciatore, da un
altro portafoglio, da una distribuzione.

Il primo criterio che avevo scritto **non poteva rispondere**: usava l'indice del primo scambio
archiviato, e quel campo non esiste nei file. Il test e' girato su 43.000 posizioni e ha
risposto «0 giudicabili». Me ne sono accorto solo perche' stampo sempre il denominatore —
senza quello avrei letto uno zero come una risposta.

## La risposta, su 116.330 posizioni

| | quante | quota |
|---|---|---|
| **gettoni RICEVUTI, mai comprati** | 57.108 | **49,1%** |
| **buco nostro, colmabile** | 59.222 | **50,9%** |

**Meta' e meta'.**

## Cosa significa, in numeri

- **Il 100% e' impossibile per costruzione.** Anche con un recupero perfetto, circa il 21% di
  tutte le posizioni resta non giudicabile: quegli acquisti non sono «non ancora raccolti»,
  sono **mai avvenuti su un mercato**. Aspettare il 100% sarebbe aspettare per sempre.
- **La meta' colmabile vale molto.** Oggi le posizioni complete sono circa il 14%. Recuperando
  quella meta' arriverebbero intorno al 33%: **due volte e mezzo** il materiale su cui si puo'
  calcolare chi ha guadagnato.
- **E intanto non si aspetta niente.** Le posizioni chiuse sono complete per costruzione:
  7.916 portafogli su base e 17.813 su robinhood. L'analisi parte da la', adesso.

## La regola che ne esce

Le posizioni incomplete **non vanno fra i perdenti: vanno fra gli SCONOSCIUTI**, con scritto
perche'. E d'ora in poi la completezza si verifica **per singola moneta**, non per portafoglio:
dello stesso portafoglio si usa la posizione sulla moneta A e si scarta quella sulla moneta B.
