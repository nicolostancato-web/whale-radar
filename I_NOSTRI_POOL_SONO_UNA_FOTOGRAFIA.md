# I nostri dati del mercato pubblico sono una fotografia di pochi minuti — 7 ottobre 2026

## Il fatto

Misurando perché solo il 2,4% delle posizioni nel pool riusciva ad avere un importo in denaro,
sono risalito alla causa, ed è nei **nostri** dati, non nella chain:

| un pool d'esempio | |
|---|---|
| righe nel nostro file degli scambi | 300 |
| arco di blocchi coperto | **531 blocchi = 54 secondi** |
| trasferimenti veri di quel gettone | 18.964, su **10 milioni di blocchi** |
| movimenti di mercato dopo la fine del nostro file | **11.207 su 11.663 (96%)** |

E non è un caso isolato. Su un campione di 12 file:

| | |
|---|---|
| arco coperto, mediana | **8,9 minuti** |
| file sotto i 5 minuti | 5 su 12 |
| file con una sola riga | 2 su 12 |

**Tutto il nostro lato pool è una fotografia dei primi minuti di vita di ogni pool, non la sua
storia.** Vale per le 49.753 raccolte nello storico.

## Perché conta più di quanto sembri

Ogni analisi fatta finora sul lato pool — le posizioni dei candidati, il fondale onesto sui pool,
i multipli calcolati lì — è stata calcolata **su quei primi minuti**. Non è sbagliata: è di
portata molto più piccola di quanto il nome «posizioni nel pool» suggerisse.

E spiega perché il collegamento col denaro riusciva solo nel 2,4% dei casi: per il 96% dei
movimenti di mercato **non avevamo l'altro lato**.

## La soluzione, misurata subito

Gli scambi Uniswap v4 si possono chiedere **per singolo pool** con un filtro sull'indirizzo del
gestore e l'id del pool nel secondo argomento — e col filtro per indirizzo l'RPC accetta finestre
da 10 milioni di blocchi.

Provato sullo stesso pool:

| | nostro file | una chiamata sola |
|---|---|---|
| righe | 300 | **7.783** |
| arco coperto | 54 secondi | **11,6 giorni** |
| tempo | — | **2,5 secondi** |

**Ventisei volte i dati, in una chiamata.** È la terza volta in due giorni che la stessa mossa
— *filtrare per indirizzo invece che per tipo di evento* — moltiplica quello che possiamo leggere:
prima l'elenco dei lanci (da 34.096 chiamate a 7), poi i trasferimenti dei gettoni (da centomila
blocchi a una chiamata), adesso gli scambi dei pool.

## Il prossimo passo

Un agente che legge gli scambi di ogni pool graduato con quella chiamata, e li incrocia con i
trasferimenti già raccolti. A quel punto, per la prima volta, una posizione nel mercato pubblico
avrà **la storia intera** invece dei primi minuti — ed è lì che la strada rimasta aperta si gioca.
