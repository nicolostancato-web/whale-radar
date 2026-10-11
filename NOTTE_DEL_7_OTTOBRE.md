# La notte del 7 ottobre: quattro dubbi risolti, nessun risultato nuovo

## In una riga

Non ho trovato nulla di nuovo sul guadagno. Ho **riparato quattro difetti di misura** che avrebbero
falsato tutto quello che viene dopo, e tre di questi li ho trovati **prima** di costruirci sopra.

## I quattro difetti

**1. «Zero scambi Uniswap v4» — era un rifiuto stampato come zero.**
Avevo scritto `len(lg) if lg else 0`: una query rifiutata torna `None`, e quella formula la stampa
come `0`. Gli scambi v4 ci sono in tutta la storia (960-4.321 ogni mille blocchi). Nona volta in
due giorni che un'assenza diventa un fatto, e la lezione era già scritta da me dentro l'agente:
**una lezione scritta nell'agente non protegge chi lavora a mano accanto all'agente.**

**2. Il numero delle monete graduate «ballava» (5.169 → 11.489 → 12.970).**
In un punto contavo monete, nell'altro pool. Sono **5.268 monete** e **13.709 pool**, 2,6 pool per
moneta. Non un dato sbagliato: **un nome sbagliato.** Lo 0,78% di graduazione regge.

**3. «Zero vendite al pool» su monete che scambiavano eccome.**
Su Uniswap v4 un pool **non ha indirizzo**: i gettoni si muovono verso un unico contratto gestore,
`0x8366a39cc670b4001a1121b8f6a443a643e40951`. Confrontavo identificativi da 64 cifre con indirizzi
da 40: non potevano combaciare mai. Trovato il gestore sulla chain, vendita e travaso sono
finalmente separati: **75,8% vende sul mercato, 20,6% travasa altrove, 2,8% non muove niente.**

**4. Un file che mescolava due logiche.**
Scrivo in aggiunta, e avevo cambiato le regole: righe vecchie e nuove nello stesso file, e il tasso
di vendita passava da 76,6% a 26,9% senza che si vedesse. **Un file che mescola due logiche è
peggio di un file vuoto, perché sembra pieno.** Messo un numero di versione: quando la logica
cambia, si butta e si rifà.

E un quinto, della stessa famiglia dei primi tre: il gestore dei pool lo riconoscevo solo per le
monete presenti nel mio elenco locale, **mentre è un contratto unico per tutta la chain**. Tre
volte in una notte la stessa forma: **un fatto globale trattato come se fosse locale.**

## L'unica cosa interessante trovata, e ridimensionata subito

Una moneta aveva il 95% dei trasferimenti da un solo mittente: un portafoglio che ha **regalato i
gettoni a 43.024 indirizzi diversi**, ricevendone solo 8. Una distribuzione di massa, reale e
documentata — proprio il meccanismo che Nicolò aveva parcheggiato come «l'altro mondo», e che
invece succede qui.

Ma su un campione di 14 monete la quota mediana del mittente principale è **38%**, e **nessuna**
supera la metà. Quindi: il caso esiste, **non è la regola**, e generalizzarlo da un esempio sarebbe
stato l'errore di tutta la giornata.

## Dove siamo

| | |
|---|---|
| curva: strategia copiabile | **chiusa** (nessuna cosa eseguibile supera 1) |
| mercato pubblico | **misurabile adesso**, per la prima volta |
| monete lette nel mercato pubblico | 232 su 5.268 |
| cosa manca | copertura, e il lato denaro degli scambi nel pool |

Il lavoro della notte non ha prodotto un numero. Ha prodotto **la possibilità di fidarsi del
prossimo numero**, che dopo i sei risultati smontati di ieri vale più di un numero in più.
