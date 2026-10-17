# Il motore delle combinazioni — primo risultato, e il vincolo che lo governa

**30/09 notte. Costruito dopo aver ritrovato nei trascritti una direttiva di Nicolo' del 23/09
che avevo perso per sette giorni.**

## La direttiva perduta

> «Io mi aspetto una strategia mostruosa, dove si analizzano migliaia di combinazioni tutte
> perfette. Entriamo quando la pressione e' X%, poi si concatena con una percentuale costi cosi',
> oppure una percentuale di buyer che subentra in base alla liquidita', e poi si interseca questo
> settore. Una roba molto piu' complicata, tecnica, tutta fatta di parametri incrociati.»
> — Nicolo', 23/09

Il 30/09 gli ho portato «compra al 5° scambio, $25, tieni una settimana»: **una manopola sola.**

## Come e' costruito, e le tre difese obbligatorie

Provando migliaia di combinazioni **se ne trova sempre una che sul passato sembra oro**: non e'
un rischio, e' una certezza matematica. Quindi:

1. **Tre pezzi di tempo, non due.** Si cerca sul primo (45%), si scegli sul secondo (27%), si
   giudica sul **terzo** (28%), che non e' stato usato ne' per cercare ne' per scegliere.
2. **Il controllo sul rumore.** La stessa ricerca gira su esiti **mescolati**, dove per
   costruzione non c'e' niente da trovare. Se la migliore sul vero non batte la migliore sul
   rumore, abbiamo trovato il rumore. Questo numero si stampa sempre.
3. **Quante ne ho provate.** Dichiarato: **10.700** combinazioni di 1-3 condizioni incrociate.

Le condizioni usano **solo** attributi noti prima di comprare.

## Il risultato su robinhood

**La combinazione:** `gap_mediano < 2,5` **E** `caduta_dal_massimo ≈ 0` **E**
`scambi_per_portafoglio < 1,2`

In parole: **il pool scambia a raffica, ogni portafoglio compra una volta sola, e il prezzo e'
al suo massimo.**

| | combinazione | fondale |
|---|---|---|
| media | **+193,8%** | +17,9% |
| **mediana** | **+103,7%** | +0,4% |
| in pari | 76% | 51% |
| fanno +100% | 51% | — |
| senza il 10% migliore | +119,2% | — |
| pool | 157 | 7.681 |

**Non e' un effetto di coda:** la mediana raddoppia, e togliendo il 10% migliore resta +119%.

**Contro il rumore:** la migliore sui dati mescolati fa +55,4% nel caso piu' fortunato su cinque
prove. Il vero la batte di piu' di tre volte.

## IL VINCOLO CHE GOVERNA TUTTO

Tutti i 157 pool hanno `eta_ore = 0,017`: **esattamente un minuto.** Sei scambi con un secondo
di distacco, **sei portafogli distinti**, prezzo al massimo.

**Per entrarci dovrei comprare come settimo, entro sessanta secondi dalla nascita del pool,
competendo con i bot che hanno fatto quei sei scambi.**

E qui sta il limite della misura: **assumiamo latenza zero.** Diamo per scontato di comprare al
prezzo del sesto scambio, mentre in una raffica da un secondo il prezzo si muove mentre decidiamo.

> **Un vantaggio che esiste solo a latenza zero non e' un vantaggio: e' una gara di velocita'
> contro chi ha i server nel datacenter giusto.**

## Su base: non concludente

Migliore sul pezzo di scelta +48,5%, rumore +25,6%: batte, ma solo di due volte. E sul pezzo di
giudizio restano **33 pool**: non si giudica.

**Un ingrediente e' comune a entrambe le chain:** `scambi_per_portafoglio < 1,2` — tanti
portafogli diversi che comprano una volta sola. Non e' un caso: e' la firma della
partecipazione ampia.

## Cosa faccio stanotte

1. Misurare **quanto costa la latenza**: rifare il conto comprando al prezzo dello scambio
   successivo, e di due scambi dopo. Se il vantaggio sopravvive a tre secondi di ritardo, vale.
2. Cercare combinazioni **senza la condizione di velocita'**, per vedere se esiste un pattern
   raggiungibile da un umano o da un bot lento.
3. Farla bocciare da Astra e da Grok.
