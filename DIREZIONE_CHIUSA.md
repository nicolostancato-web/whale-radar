# Comprare memecoin nuovi da taker: direzione CHIUSA


> ## ✅ RIMISURATO IL 26/09 — la direzione resta chiusa, ma per una ragione diversa
>
> I numeri di questo documento erano sbagliati **quattro volte**: la finestra di osservazione, il
> criterio di scarto, il verso dei prezzi, e la taglia mai misurata. Corretti tutti e quattro, la
> conclusione non cambia — ma le ragioni scritte sotto sono quelle vecchie, e non valgono.
>
> **Il quadro vero (robinhood, pool giudicabili, uscita al prezzo mediano delle vendite):**
>
> | | valore |
> |---|---|
> | pool da cui NON si esce mai | **17,1%** (non 42%: quello era la mia regola «meno di 5 vendite») |
> | fondale | **−9,5%** (non −29,9%) |
> | miglior condizione gratuita fuori campione | **−2,9%** (oltre 15 compratori nelle prime 2 ore) |
> | media dei pool con un prezzo misurato | +9,2%, ma **−1,4% di mediana** e il 57% sotto zero |
>
> **Perche' resta chiusa.** Il fondale e' molto meno ostile di quanto credessimo, e i segnali
> osservabili prima di comprare lo migliorano **in modo monotono e pulito** — piu' compratori nelle
> prime due ore, meno pool senza uscita (dal 30% al 10%) e media meno negativa (da −18% a −3%).
> **Ma nessuna fascia arriva sopra zero**, ne' col numero di compratori, ne' con la capienza in
> dollari, ne' con un bersaglio alto.
>
> **E i multipli che esistono non hanno capienza:** nei pool che toccano il 10x, sopra quel prezzo
> sono passati in mediana **32 dollari**. Dodici su quindici sotto i cento.
>
> Otto strategie, otto morte, **zero euro rischiati** — e stavolta con strumenti di cui ci si puo'
> fidare. Il dettaglio di H6/H6b e delle quattro lezioni e' in `VERDETTO_H6.md`.
>
> *Tutto cio' che segue e' stato misurato col metro vecchio e va letto come cronaca, non come dato.*

> ## ⚠️ IL METRO, CORRETTO DUE VOLTE IN UN GIORNO (25/09)
>
> **La mattina** ho trovato un difetto vero: misuravo l'esito a fine orizzonte su pool di cui
> avevamo poche ore di dati, quindi chi non aveva vendite *perche' non stavamo guardando* finiva
> fra le trappole. Ho scritto che le trappole vere erano il 14,4% invece del 30%, e che il mercato
> perdeva un decimo invece di un terzo. **L'ho annunciato prima di verificarlo.**
>
> **La sera la correzione si e' rivelata peggiore del difetto.** Avevo definito «giudicabile» come
> *«di questo pool abbiamo visto N ore di scambi»*. Ma un pool muore smettendo di scambiare: le ore
> osservate sono poche **proprio perche' e' morto**. Quel criterio non toglieva i pool poco
> osservati — toglieva i morti, cioe' esattamente le trappole. Sopravvivenza travestita da rigore.
>
> Il criterio giusto e' una data e non sa nulla di come e' andata: **il pool e' giudicabile se e'
> NATO abbastanza prima della fine della raccolta.** Se poi e' morto in dieci minuti, quello e' il
> suo esito, non un motivo per escluderlo.
>
> | chain (orizzonte 24h) | criterio «ore viste» (sbagliato) | **criterio «eta'» (giusto)** |
> |---|---|---|
> | robinhood | 35,2% trappole su 42% del campione | **42,6% su 96%** |
> | base | 47,4% trappole su 43% del campione | **53,0% su 98%** |
>
> **I numeri veri sono peggiori di tutto quello che avevo scritto finora:** trappole **43-53%**,
> media **−41% / −52%**. La direzione non e' solo chiusa, e' chiusa con piu' margine di quanto
> credessimo. Le tabelle qui sotto, prese col metro vecchio, sono ottimistiche.
>
> **La lezione, in positivo: quando scarti dei casi, chiediti se il motivo dello scarto sa gia'
> come e' andata a finire.** Se lo sa, non stai pulendo il campione: lo stai scegliendo.
> Scritta in `agents/insieme.py`, `agents/cercatore.py`, `agents/lag_wallet.py`.
>
> *Le tabelle sotto restano com'erano scritte: servono a ricordare con quale metro sono state prese, non a essere citate.*
> prese, non a essere citate.*

*24 settembre 2026, notte. Cinque giorni, sette strategie, zero euro rischiati.*

## Il verdetto, in due numeri

**I pool da cui si riesce a uscire rendono +1,1%.** Le trappole sono il 10% anche nel nostro punto
migliore, e costano il 98%.

```
0,90 × (+1,1%) + 0,10 × (−98%) = −8,9% per operazione
```

Per andare in pari servirebbero trappole sotto l'**1,1%**. Siamo al 10,3%: **manca un fattore nove**.

Misurato sul sottoinsieme fuori campione, con la media di portafoglio (non la mediana) e le trappole
dentro la stessa media. **Tutti e dieci i decili del modello sono negativi.** Togliendo l'1% migliore
peggiorano tutti.

## L'errore che nascondeva il verdetto

Per un giorno ho creduto che servisse scendere sotto il 2,7%, perche' usavo il +2,7% dei pool sani
«in generale» insieme al 10% di trappole del modello selettivo. **Due sottoinsiemi diversi.**
Sullo stesso insieme i sani rendono **+1,1%**, e la soglia diventa 1,1%.

Trovato da Grok prima di vedere i dati: aveva previsto −7,4% a operazione, misurato −8,9%.

## Tutte le porte provate

| cosa | esito |
|---|---|
| 36 caratteristiche del flusso degli swap | il modello si ferma al 10% di trappole |
| «almeno una vendita gia' avvenuta» (filtro gratuito) | 35% → 21%, costa il 2% dei sani. **Il migliore.** |
| proprieta' del token rinunciata (12x!) | cattura solo il 24% delle trappole → ridondante |
| token con piu di una pool | peggiora in combinazione (35,1% contro 32,4%) |
| permessi degli hook V4 | i pool con hook hanno MENO trappole, non piu' |
| ritiro della liquidita' prima della decisione | 22% contro 29%: **nessuna differenza** |
| uscita alla prima occasione utile | **−32,9%**, peggio del −32,7% |
| sette regole di uscita (bersagli fissi, stop mobili) | tutte peggiorano |

## La legge che spiega tutti i fallimenti

**Un segnale puo' essere enorme in rapporto e inutile in copertura.** (Grok, 24/09)

Per portare le trappole dal 10% all'1,1%, un filtro deve catturare circa l'**80% delle trappole
residue** scartando non piu' del **5% dei sani**. Il nostro segnale piu' forte — la proprieta'
rinunciata, 12 volte piu' frequente fra le trappole — ne cattura il **24%**.

| trappole catturate | sani persi | valore atteso |
|---|---|---|
| 30% | 5% | −4,9% |
| 50% | 5% | −2,9% |
| 70% | 5% | −0,7% |
| **80%** | **5%** | **+0,4%** |

**Il rapporto non e' la copertura.** E' l'errore che ho ripetuto tre volte in un pomeriggio.

## La struttura del problema, che resta vera

Le trappole sono due famiglie, meta' e meta':

- **famiglia A (52%)**: nessuno era MAI riuscito a vendere. **Si evitano gratis.**
- **famiglia B (48%)**: si vendeva, poi le vendite si azzerano. Prima della decisione sono
  **indistinguibili** dai pool sani — 6 compratori e 16 vendite contro 7 e 18.

L'interruttore della famiglia B **non e' istantaneo**: il 55% ha almeno una vendita dopo il nostro
ingresso, meta' entro sette minuti. Ma uscire li' non salva il conto, perche' il primo prezzo di
vendita dopo l'acquisto e' quasi sempre sotto il nostro.

## Cosa resta, e vale piu' delle sette strategie

1. **Un metro che misura i soldi**: esito sui prezzi di chi VENDE, non sulla mediana di tutti i
   print — che dice quanto pagano gli altri per entrare.
2. **Il fondale vero**: comprare e rivendere memecoin nuovi perde circa un terzo.
3. **La mappa entrata/tenuta**: prima si entra e piu' si tiene, meglio e'. Monotono su 25 caselle.
4. **36 caratteristiche** estratte dagli stessi dati che avevamo da mesi (prima erano 5 contatori).
5. **La liquidita' dei pool V4 si legge** (85% del nostro mondo, dichiarato irraggiungibile il 23/09).
6. **Due revisori indipendenti** che hanno trovato quattro errori che io non potevo vedere.
7. **La legge rapporto-contro-copertura**, che d'ora in poi si applica prima di entusiasmarsi.

## Cosa si apre

I nostri stessi conti dicono dove sta la rendita: **chi entra nei primi blocchi mette dentro il
6,26% del volume e chiude in utile nello 0% dei casi** — sono i portafogli di chi lancia, che
fabbricano domanda. La controparte che guadagna **non e' un taker che arriva mezz'ora dopo**.

Qualunque cosa si apra, non e' un altro filtro sul nastro degli scambi.

---

# Il limite scoperto per ultimo: non sappiamo CHI

*25 settembre, notte. Emerso provando l'ultima strada indicata da Astra.*

Astra aveva corretto una mia conclusione: avevo scritto che la famiglia B e' **imprevedibile**, e
invece avevo solo dimostrato che non e' prevedibile **con i descrittori provati**. Indicava quattro
posti non esplorati, e il piu' promettente era l'**attribuzione economica**: chi crea il token, chi
finanzia chi lo crea, e soprattutto — se le vendite che il nostro filtro conta siano di compratori
indipendenti o di indirizzi del creatore.

**Provato, e si e' rivelato impossibile con i dati attuali.**

Il campo che uso come «chi ha fatto lo scambio» registra, nell'81% dei casi, `v4:sender` — cioe'
**chi ha chiamato il contratto: il router, non la persona**.

La prova sta nei numeri:

| | |
|---|---|
| l'indirizzo piu' frequente | **42,6% di TUTTI gli scambi** |
| indirizzi distinti | 2.001 su 44.804 scambi |
| un singolo indirizzo compare in | **6.202 pool diversi** |

Nessun trader si comporta cosi'. Sono le porte, non le persone.

**Cosa questo invalida:** tutto cio' che in cinque giorni ho chiamato «compratori distinti»,
«portafogli nuovi», «scambi per portafoglio» misurava **router**, non gente. Spiega perche' il
segnale «la folla sta arrivando» non era davvero un segnale di folla.

**Cosa NON invalida, ed e' la parte che conta:** il verdetto di chiusura non usa i portafogli. Usa
prezzi ed esiti — pool sani a +1,1%, trappole al 10%, risultato −8,9% per operazione. **Quel conto
regge.**

**Cosa serve per riaprire l'attribuzione:** l'iniziatore della transazione (`tx.origin`), che non
raccogliamo. E' recuperabile — l'identificativo della transazione ce l'abbiamo — ma e' una raccolta
nuova su milioni di operazioni.

**Settima volta in cinque giorni** che un buco nei dati si scopre solo provando a usarli. E come le
altre sei, l'ha rivelato una domanda posta da fuori.
