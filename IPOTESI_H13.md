# H13 — quando uscire, non cosa comprare

**Registrata il 29/09, prima di guardare qualunque risultato sulle uscite.**

## La leva che in dodici ipotesi non abbiamo mai toccato

Tutte e dodici hanno variato **quale pool comprare**. Nessuna ha variato **quando uscire**:
ogni misura fatta finora e' «compra e tieni fino alla fine della finestra», cioe' resta dentro
anche mentre il pool muore sotto gli occhi.

Non era una scelta: il dato non conteneva il cammino del pool, solo il suo punto d'arrivo.
Da oggi lo contiene (`_cammino`: ore dall'ingresso, prezzo, valuta, per ogni vendita).

Una regola d'uscita **non e' selezione col senno di poi**: usa quello che si sa in quel momento.

## Perche' potrebbe contare

Il pool tipico perde poco; la media perde molto. Sul decimo migliore a 168 ore:

| | media tagliata | mediana |
|---|---|---|
| robinhood | −17,1% | **−3,6%** |
| base | −20,7% | **−3,3%** |

**Tutta la distanza fra −3% e −17% e' una minoranza che muore del tutto.** Chi tiene fino alla
fine se la prende per intero, per costruzione.

## L'ipotesi

> **H13: una regola d'uscita fissata in anticipo — si esce quando il prezzo scende sotto una
> soglia rispetto all'ingresso — porta il decimo migliore sopra il fondale di almeno 10 punti,
> fuori campione, su tutte e due le chain.**

## Come muore, deciso prima

1. **Si sceglie UNA soglia sola**, sulla prima meta' dei dati per data di nascita. Non si
   prova una griglia e si tiene la migliore: e' cosi' che si compra rumore.
2. Si giudica sull'altra meta', **mai vista**, e quel numero e' il verdetto.
3. Serve su **tutte e due le chain**. Una sola e' rumore.
4. Si giudica solo sull'incasso da $500 veri, mai sul prezzo.
5. **Il costo di uscita si paga**: uscire in fretta in un pool sottile costa, e va contato
   come si conta all'entrata.

## La trappola che mi aspetto, scritta prima di caderci

Provando regole d'uscita ne troverò decine che sul passato funzionano. La differenza fra una
regola e un ricordo del passato è che la regola si sceglie **prima** di vedere come è andata.
Se mi ritrovo a scrivere «proviamo anche a −40% invece di −50%», ho già sbagliato.

## Nota su una cosa vista oggi e NON creduta

Alla finestra da un mese, su robinhood, il decimo migliore fa **+2,7% fuori campione**. Sono
**ventuno pool**, e su base lo stesso calcolo fa −23,4%.

Per la regola scritta stamattina, questo **non conta**. Soglia per tornarci: almeno **2.000
pool fuori campione** e positivo su **tutte e due** le chain. Fissata ora, prima di averli.
