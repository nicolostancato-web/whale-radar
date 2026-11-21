# Da dove vengono i gettoni di chi vende nel crollo

**11 ottobre. Terza versione di questo documento, e le prime due erano sbagliate.** Tengo qui
anche i numeri ritirati, perché sapere *come* un numero è caduto vale quanto il numero.

## La risposta, su 29 crolli e 85 venditori

| da dove arrivano i gettoni venduti | media | mediana | a ≥90% |
|---|---|---|---|
| **da un altro indirizzo** | **43,2%** | 42,1% | **18 su 85** |
| dal pool, dopo la promozione | 34,2% | 24,5% | 14 su 85 |
| dalla curva, prima della promozione | 22,6% | 1,7% | 12 su 85 |
| coniati | 0% | 0% | 0 |

E sul crollo stesso: il venditore più grosso fa in mediana il **17%** del venduto, e il **24%**
del venduto viene da chi aveva comprato nel primo minuto.

**La strada principale non è la curva: è un trasferimento da un altro indirizzo.** Diciotto
venditori su 85 hanno ricevuto almeno il 90% dei loro gettoni così. Vuol dire che la catena va
indietro di un passo: chi ha venduto non è chi ha comprato, e la domanda diventa *chi lo ha
fornito*.

## Cosa ritiro, e perché era sbagliato

**Ritirato: «metà dei venditori grossi aveva comprato sulla curva» (26 su 54).** Quel conto
partiva dal `from` della transazione, e il `from` della transazione **non è il venditore**: su
Uniswap v4 chi chiama lo scambio è di solito un router. Lo si vedeva già dal fatto che il 36% di
quegli indirizzi non appariva in **nessun** trasferimento del gettone — un indizio che avevo
registrato come «non misurabile» invece di prenderlo per quello che era: la prova che stavo
guardando la persona sbagliata.

Grok, interrogato in parallelo sulla documentazione di Doppler e Uniswap, lo dice con la fonte:
*«il `sender` è chi ha chiamato `PoolManager.swap` e ha ricevuto la callback, di solito il
router, non il portafoglio finale. Il `Transfer` ERC-20 esce dal `PoolManager` nella stessa
transazione.»*

**Ritirati prima ancora: «il venditore più grosso fa il 51%»** (calcolato su 4 crolli su 27,
perché negli altri la ricerca falliva — e i 4 che riuscivano erano i crolli con pochi scambi,
cioè proprio quelli dove un venditore pesa tanto per costruzione), e **«il 10,3%»** (misurava i
**compratori**, perché nel mio codice il verso degli scambi era invertito).

## Come adesso il venditore è quello giusto

Si prende dal **trasferimento del gettone dentro la stessa transazione**: in una vendita il
gettone entra nel pool, quindi il mittente di quel trasferimento è chi possedeva i gettoni.

Il punto cieco è passato **dal 36% a 2 casi su 87**. E costa meno di prima: sono sparite tutte le
chiamate al nodo che servivano a chiedere il mittente, perché i trasferimenti si leggevano già
per la provenienza. Più giusto e più economico insieme.

## Il prossimo passo, che i dati indicano da soli

I 18 venditori che hanno ricevuto tutto da un altro indirizzo sono l'unico gruppo con una
struttura: seguire **un passo indietro** e vedere chi li ha forniti, e se lo stesso fornitore
compare su più monete. Se compare, è un'entità che si muove dietro più lanci — e quella si vede
prima.

## Aggiunta dell'11 ottobre, notte: quel 43% è quasi tutto infrastruttura

Ho etichettato ogni fornitore guardando se all'indirizzo c'è del codice. Su 85 venditori:

| i gettoni venduti arrivano | media | a ≥50% |
|---|---|---|
| **da un contratto** (router, portafoglio intelligente) | **58,4%** | **51 su 85** |
| da una persona | **7,5%** | 7 su 85 |

**Quindi la domanda «da dove prendono i gettoni» non si risponde a questo livello.** Per la
maggior parte dei venditori la catena passa attraverso contratti: il possessore vero sta dietro
un portafoglio intelligente, e l'indirizzo che vedo è idraulica della chain, non una persona.

Lo stesso vale per i fornitori che sembravano ricorrenti: quattro comparivano su 20, 18, 11 e 10
monete su 29 — e sono **tutti contratti**. Di 63 fornitori distinti, uno solo che compare su più
di una moneta è una persona.

**È «ordinare seleziona gli artefatti» in forma nuova:** una classifica per ricorrenza mette in
cima l'infrastruttura per costruzione, perché l'infrastruttura è esattamente la cosa che ricorre.

**Cosa servirebbe per andare oltre:** risolvere la proprietà dei portafogli intelligenti, cioè
risalire dal contratto a chi lo controlla. Non è impossibile, ma è un lavoro diverso e più
profondo del seguire i trasferimenti — e prima di farlo vale sapere che i casi con un fornitore
umano sono **7 su 85**.
