# ⚖️ VERDETTO — LOOP 1 è riuscito, va avanti, o va chiuso?
*2026-09-05 07:02 UTC · criteri scritti il 2026-09-03, **prima** di vedere questi risultati*

> Questi criteri esistono per un motivo solo: rendere **impossibile spostare il traguardo.**
> Il rischio più grande non è sbagliare una strategia — è continuare ad aggiungere segnali
> finché qualcosa appare verde per caso.

## Cosa serve per dire «riuscito»

| condizione | soglia |
|---|---|
| rendimento netto | **≥ 10%** |
| significatività (t) | **≥ 2.0** |
| **prove indipendenti** | **25** (gruppi, non righe) |
| righe minime | 250 |
| configurazione | congelata **prima** di guardare |
| holdout | mai visto, **1 sola lettura** |
| costi | condizionati alla liquidita' al momento dell'uscita, gambe separate, trappole a -100% |

## Cosa succede se non ci arriviamo

Scadenza: **2026-10-03** (fra 27 giorni) oppure **500 trade** accumulati in validazione, quello che viene prima.

> non 'il progetto e' fallito', ma 'questo mercato non offre un edge sfruttabile con il nostro approccio'. E' un risultato, non una sconfitta: dice dove NON cercare.

## Perché le prove si contano a gruppi

> raggruppando per GIORNATA e per CREATOR: cio' che nasce lo stesso giorno o dalla stessa mano si muove insieme, quindi conta UNA volta. Cento trade legati allo stesso evento non sono cento prove.

> non e' un numero scelto a caso: per distinguere un effetto del +10% dal rumore, con una dispersione fra giornate dell'ordine del 25%, servono circa (2*25/10)^2 = 25 gruppi indipendenti perche' il t arrivi a 2. Fissato PRIMA di guardare i risultati.

> Esempio misurato: 200 righe raggruppate in 8 giornate danno **t = +0,58**. Contando le righe
> lo stesso dato darebbe **t = +2,88** — cioè la differenza fra «non abbiamo trovato niente» e
> «abbiamo trovato qualcosa». Cinque volte più generoso, e sempre nella direzione che ci fa
> comodo.

## Divieti in vigore

- vietato riottimizzare una configurazione dopo averla congelata
- vietato leggere l'holdout piu' di una volta per configurazione
- vietato allargare un filtro che non generalizza per farlo sembrare migliore
- vietato aggiungere una pista nuova mentre una vecchia e' in attesa di verdetto
- vietato spostare queste soglie: se cambiano, va scritto in DECISIONS.md con la data e il motivo
- vietato contare le righe come prove: il t si calcola sui gruppi (giornata, creator)
- vietato dichiarare un risultato senza aver verificato che il segnale fosse DISPONIBILE prima dell'ingresso, con il ritardo reale del bot

## Configurazioni congelate

| chain | congelata il | holdout già letto |
|---|---|---|
| robinhood | 2026-09-03 | no |

## Stato oggi

> ⏸️ **Nessuna pista ha ancora una configurazione congelata**, quindi non c'è niente da
> giudicare. La fascia di validazione è troppo giovane: il verdetto arriverà quando avrà
> abbastanza trade, non quando ci farà comodo guardarla.