# La coda esiste e non paga — 25 settembre, sera

*Ultima domanda aperta sulla direzione «comprare memecoin nuovi da taker». Zero euro rischiati.*


> ## 🔴 SOSPESO IL 25/09 A MEZZANOTTE — I NUMERI QUI DENTRO SONO CONTATI COL SEGNO SBAGLIATO
>
> Questo documento chiude la direzione basandosi sul fatto che i pool sani rendono **+0,9%**.
> Quel numero e' stato calcolato contando **gli acquisti come vendite** nel 73% dei pool: il codice
> usava `a0 > 0` per dire «vendita», ma quale dei due token sia il memecoin dipende dall'ordine
> alfabetico degli indirizzi, e cambia da pool a pool (vedi `agents/verso.py`).
>
> Col verso corretto, sugli stessi pool di robinhood con un prezzo davvero misurato:
>
> | | col segno sbagliato | **col verso corretto** |
> |---|---|---|
> | media | +0,45% | **+9,20%** |
> | media togliendo l'1% piu' alto | — | **+3,71%** |
> | intervallo 5-95% (bootstrap) | arrivava a zero | **+7,4% … +11,0%** |
> | mediana | −2,28% | −1,36% |
>
> Il pareggio passa da «trappole sotto lo 0,9%» a **«sotto l'8,6%»** (3,6% col dato tagliato), e il
> tasso da battere e' il 36,4%. **Manca un fattore quattro, non cinquanta.**
>
> Su base invece regge: media +1,83% che tolto l'1% alto diventa **−0,35%**. Quella chain resta muta.
>
> **La direzione non e' piu' chiusa da questi numeri.** Non e' nemmeno aperta: e' da rimisurare
> daccapo. Nulla di quanto scritto sotto va citato finche' non e' rifatto.
>
> **La lezione, in positivo: prima di dare un segno a una quantita', stabilisci a quale token
> appartiene.** Il difetto e' rimasto invisibile per giorni perche' `insieme.py` e `cercatore.py`
> calcolavano il prezzo *uno l'inverso dell'altro* e nessuno dei due era assurdo da solo.

## La domanda

Col metro corretto, i pool sani rendono **+0,9%** (robinhood) e **+0,2%** (base) uscendo al prezzo
mediano di chi ha venduto. Troppo poco per pagare il 43-53% di trappole, qualunque filtro si
inventi. Restava una via: **non uscire alla mediana, ma tenere per la coda** — pochi pool che fanno
5x o 10x prima di morire. E' l'ipotesi del paper-bot parcheggiata ad agosto.

## La misura

Ho aggiunto `_max_vendibile`: il massimo dei **soli prezzi di vendita** dopo la decisione. Non il
massimo del prezzo — quello e' un prezzo a cui qualcuno *comprava*, non a cui io potevo vendere.
Stesso metro dell'uscita, cosi' i due numeri si confrontano senza trucchi.

E' un limite superiore generoso: presuppone di aver venduto **nel punto esatto**, e ignora
l'ordine in cui le cose accadono. Se anche cosi' non paga, non paga.

## Il risultato

| bersaglio | robinhood: lo tocca | valore atteso | base: lo tocca | valore atteso |
|---|---|---|---|---|
| +25% | 11,3% | **−42,8%** | 3,9% | **−52,6%** |
| +50% | 6,3% | −42,1% | 2,8% | −52,1% |
| +100% | 3,2% | −41,4% | 1,7% | −51,6% |
| +400% | 0,8% | −39,9% | 0,9% | −49,1% |
| +900% | 0,4% | **−38,7%** | 0,8% | **−45,4%** |

**La coda c'e' davvero**: lo 0,4% dei pool arriva a +900%, il massimo osservato e' +2.000%.
**E non sposta niente.** Portare il bersaglio da +25% a +900% migliora il valore atteso di quattro
punti su robinhood — da −42,8% a −38,7% — e lascia il segno meno dov'era.

Il conto e' semplice: `0,004 × 9 = +3,6%` contro un fondo di perdite che vale **−45%**.
La coda e' troppo sottile per pesare quanto il centro.

## Cosa resta

**Niente.** Su questa direzione le domande aperte erano tre e sono chiuse tutte:

| domanda | risposta |
|---|---|
| si possono filtrare le trappole? | nemmeno un filtro perfetto basta: il soffitto e' **+0,9%** |
| si puo' uscire meglio? | sette regole di uscita, tutte peggiori |
| paga la coda? | **no**, a nessun bersaglio fra +25% e +900% |

Otto strategie provate, otto morte, **zero euro rischiati**. E' il risultato del metodo, non il suo
fallimento: il costo di scoprirlo e' stato sei giorni di macchina gratuita invece di un conto vero.

## La lezione, in positivo

**Prima di cercare il filtro, misura il premio.** Per sei giorni ho cercato modi migliori di
separare i buoni dai cattivi, senza mai chiedermi quanto valesse un buono. Valeva +0,9%: nessuna
separazione poteva bastare, e si poteva sapere il primo giorno con una riga di codice.
Scritto in `agents/insieme.py`, dove si calcola l'uscita.
