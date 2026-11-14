# Il tasso di successo descriveva una posizione su otto

*4 ottobre 2026 · misurato dopo che Astra e Grok, indipendentemente, hanno nominato lo stesso difetto*

## Cosa avevo riportato

«Il **55,9%** di chi compra e vende guadagna» — poi, stringendo la definizione di chiusura,
«il **70%**». L'ho usato come fondale per decidere se una flotta fosse brava.

## Cosa dicono i quattro stati

Registrando ogni posizione con il suo stato, invece di contare solo chi ha comprato E venduto:

| stato | quota delle posizioni |
|---|---|
| **chiuse** (ha venduto quasi tutto) | **10-16%** |
| parziali (ha venduto una parte) | 4-7% |
| **aperte, mai vendute** | **41-43%** |
| solo uscite (vende gettoni di cui non vediamo l'acquisto) | 35-43% |

**Il tasso del 70% era calcolato su una posizione su otto.** Il 42% non è mai stato venduto e
non compariva in quel numero.

## Perché i due revisori avevano ragione, e come

**Grok:** «Chi vende i vincenti e tiene i perdenti ha un tasso alto sul passato chiuso E sul
futuro chiuso, perché il futuro entra nel campione solo quando viene venduto. Le quattro flotte
su cinque che non hanno mai venduto sono esattamente la massa che questo filtro cancella.»

**Astra, per un'altra strada:** «Il vostro conto degli attori è condizionato dalla chiusura, e
la chiusura può essere il risultato che state cercando. Create il conto al primo evento
ammissibile osservato, non alla prima chiusura né alla prima vittoria.»

Due revisori indipendenti, lo stesso punto cieco, nessuno dei due me l'aveva fatto vedere prima.

E c'è la prova interna: **stringendo** la definizione di chiusura il tasso è **salito** dal
55,9% al 70%. Un tasso che migliora quando si diventa più severi sul *vendere* misura il
vendere, non l'avere ragione.

## Il fatto nuovo che non avevo visto

**Il 35-43% delle posizioni sono «solo uscite»**: qualcuno vende gettoni di cui non vediamo
l'acquisto. O arrivano per trasferimento — e allora il costo di quella posizione è fuori dai
nostri dati — o la nostra copertura degli acquisti è incompleta.

È lo stato «non ricostruibile» che Astra ha chiesto di registrare, e non è una minoranza
trascurabile: è **un terzo del materiale**. Qualunque conto di profitto che li ignori sta
ignorando un terzo del mercato, e qualunque conto che li tratti come guadagno puro lo gonfia.

## Cosa cambia operativamente

1. **Il tasso non si riporta più da solo.** Esce sempre accanto alla ripartizione dei quattro
   stati, e il programma stampa esplicitamente che è condizionato.
2. **Il residuo resta in gettoni, mai valutato** al prezzo marginale: «un valore ricavato dal
   prezzo marginale di una pool illiquida non equivale a denaro incassabile» (Astra). È lo
   stesso errore dei «62,9 milioni» che avevo riportato come patrimonio di un finanziatore.
3. **Il database degli attori non può usare il realizzato come misura di abilità**, perché il
   realizzato esiste solo per chi ha venduto. Serve una misura che includa le posizioni aperte —
   e l'unica onesta che abbiamo è l'esito del POOL, che è quella che già usa `insider_storia`
   (verificato nel codice: registra `_bersaglio`, non la vendita della persona).

## Cosa NON è caduto

I **+19 e +18 punti** restano, perché misurano l'esito del pool e non il realizzato della
persona: il campione non è condizionato dalla politica di uscita. Su quelli pesano altre due
obiezioni ancora da testare — la sopravvivenza del capitale e la sovrapposizione fra le coorti
del controllo.
