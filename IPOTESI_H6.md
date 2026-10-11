# H6 — «il ritmo che non rallenta», registrata prima di vedere l'esito

*26 settembre 2026, notte. Prima ipotesi nata DOPO la correzione del verso dei prezzi: tutto
quello che veniva prima e' stato misurato contando gli acquisti come vendite nel 73% dei pool.*

## La regola, scritta per intero

Chain **robinhood**. Entrata 2 ore dopo il primo scambio osservato, da taker, costo 1,8%.
**Si compra solo se `ritmo_delta > -0,1453`** — cioe' se il ritmo degli scambi nella seconda meta'
della finestra di osservazione non e' crollato rispetto alla prima.
Uscita: prezzo mediano delle vendite vere entro 24 ore. Dove non esiste **nessuna** vendita,
perdita totale (−98%).

La soglia e' stata scelta sulla **prima meta'** dei dati per tempo e non va piu' toccata.

## Cosa ho gia' misurato, e cosa NON dimostra

Sulla seconda meta' (mai usata per scegliere):

| | tutti | **con la regola** |
|---|---|---|
| pool | 3.594 | 987 |
| senza alcuna uscita | 20,0% | **7,2%** |
| media | −10,36% | **+4,25%** |
| media senza l'1% piu' alto | −16,60% | **−3,66%** |
| intervallo 5–95% | −12,7% … −7,9% | **−0,6% … +9,0%** |
| mediana | −2,14% | −1,71% |

**La regola fa una cosa vera**: porta i pool da cui non si esce dal 20% al 7,2%, e questo resta in
piedi tolta la coda. **Ma il guadagno no**: la media positiva dipende da una decina di token su
987, e l'intervallo attraversa lo zero. Oggi H6 non e' un vantaggio: e' un passaggio **da
chiaramente negativo a indistinguibile da zero**.

Non e' poco — nessuna delle otto strategie precedenti ci era arrivata — e non e' abbastanza.

## La condizione di morte, scritta adesso

Su almeno **1.500 pool nuovi**, nati dopo le 00:30 del 26/09 (nessuno di quelli sopra):

1. la quota senza alcuna uscita deve restare **sotto il 10%** (oggi 7,2%, fondale 20%);
2. l'estremo basso dell'intervallo 5–95% della media deve essere **sopra zero**;
3. la media **tolto l'1% piu' alto** deve essere **sopra −2%**.

**Se anche una sola fallisce, H6 e' morta** e non si ritocca la soglia per salvarla — e' il modo in
cui sono morte le cinque prima di lei.

## Perche' potrebbe essere vera

`ritmo_delta` si misura PRIMA di comprare e guarda una cosa sola: se la gente sta arrivando o se ne
sta andando. Un pool che rallenta gia' nelle prime due ore sta morendo, e chi muore non ha
compratori a cui rivendere. Non e' una coincidenza statistica cercata fra mille: e' il meccanismo
piu' diretto possibile fra le cose osservabili al momento della decisione.

**E' anche la sua debolezza**: se funzionasse cosi' bene, sarebbe strano che nessun altro lo faccia.
La risposta onesta e' che forse lo fanno, e per questo il guadagno sparisce appena si toglie la coda.

---

## H6b — la stessa regola con un bersaglio alto (aggiunta la notte del 26/09)

Sulla stessa metà mai usata per scegliere, tenendo la regola di H6 e vendendo al primo prezzo che
tocca un bersaglio (`_max_vendibile`, cioè il massimo dei soli prezzi di VENDITA):

| bersaglio | lo tocca | media | senza l'1% più alto | intervallo 5–95% |
|---|---|---|---|---|
| nessuno | — | +4,29% | −3,55% | −0,6% … +9,6% |
| +100% | 7,1% | +0,86% | −1,93% | −2,0% … +3,6% |
| +400% | 2,2% | +4,70% | **+0,26%** | **+0,6% … +8,6%** |
| +900% | 1,5% | +11,05% | **+2,02%** | **+5,3% … +17,7%** |

**È la prima combinazione in cui la media tolta la coda resta positiva e l'intervallo non
attraversa lo zero.** Per questo va guardata con più sospetto, non con meno.

### Tre ragioni per non crederci ancora, scritte adesso

1. **Regge su quindici token.** L'1,5% di 995 pool fa 15 casi: è per questo che togliere l'1% più
   alto porta +11% a +2%. Un intervallo calcolato ricampionando gli stessi 15 eventi è ottimista
   per costruzione — misura quanto sono stabili quei 15, non quanto sono rappresentativi.
2. **Ho provato sette bersagli sulla stessa metà di prova.** Quella metà non è più vergine: serviva
   a controllare una regola, l'ho usata per scegliere un parametro. Il prossimo numero su questa
   strada deve venire da dati nuovi, non da un altro taglio di questi.
3. **Un prezzo alto non è una quantità.** `_max_vendibile` dice che *qualcuno* ha venduto a 10x, non
   che ci stava dentro una posizione. Su pool sottili quei prezzi sono spesso polvere, e questa è
   esattamente la forma dell'illusione che ci ha ingannati in agosto.

### Cosa serve prima di dire una parola in più

La **taglia** accanto al prezzo: per i pool che toccano il bersaglio, quanta valuta è passata a quei
prezzi. Sta nei dati grezzi che abbiamo già (le quantità di ogni scambio), non serve raccogliere
niente. Finché non c'è, H6b è una curiosità, non un'ipotesi.
