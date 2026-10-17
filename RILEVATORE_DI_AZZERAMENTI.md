# Non è un trova-vincenti: è un rilevatore di azzeramenti. E siamo a due punti dallo zero.

*4 ottobre 2026 · decomposizione dell'effetto su 6.140 pool di base e 21.791 di robinhood*

## La domanda che ha aperto questo

Perché l'effetto esiste su base e non su robinhood? La spiegazione comoda — «su robinhood
abbiamo meno dati, la misura è più rumorosa» — è **esclusa dai numeri**: robinhood ha più pool
(23.427 contro 6.548) e più storia per persona (mediana 42 osservazioni passate contro 16).

La differenza vera è il mercato:

| | base | robinhood |
|---|---|---|
| esito medio | **−33,7%** | −8,7% |
| posizioni che perdono tutto | **31,5%** | 9,8% |

**Su base una posizione su tre va a zero. Su robinhood una su dieci.**

## La decomposizione, su base

| | quinto peggiore | quinto migliore |
|---|---|---|
| posizioni azzerate | **57,6%** | **8,6%** |
| esito medio | −62,6% | −2,1% |
| esito medio dei **sopravvissuti** | −12,8% | **+7,0%** |

**Scarto totale +61 punti = +48 dall'evitare gli azzeramenti + 20 dalla differenza fra i
sopravvissuti.**

Quattro quinti dell'effetto sono **evitare le monete che vanno a zero**. Il segnale che abbiamo
non è «questa salirà»: è «questa non morirà».

## Il conto che indica la strada

Fra chi non si azzera, il quinto migliore fa **+7,0%**. L'esito complessivo resta −2,1% soltanto
perché l'**8,6%** va a zero comunque, e un azzeramento costa quasi tutto il capitale:

> 91,4% × (+7,0%) + 8,6% × (−97%) ≈ **−1,9%**

**Siamo a due punti dallo zero, e tutta la distanza sta in quell'8,6% residuo.**

Quindi la via a un'aspettativa positiva **non è trovare vincenti migliori**: è un **filtro
anti-azzeramento migliore**. Tagliare l'8,6% a metà porterebbe il conto sopra lo zero senza
toccare nient'altro.

## Perché è una buona notizia, e perché è un problema diverso

Prevedere quale moneta sale è difficile e dipende da informazione che non abbiamo. Prevedere
quale moneta **muore** dipende da cose **scritte nel contratto**:

- chi può stampare nuovi gettoni;
- se la liquidità è vincolata o si può ritirare domani;
- se la vendita si può bloccare;
- lo storico di chi l'ha lanciata: quante monete ha fatto, come sono finite.

È esattamente la famiglia di dati che avevo elencato il 1 ottobre fra le cose «che esistono nel
mondo e non guardiamo» — e che non ho mai raccolto, perché ho inseguito prima le squadre, poi i
portafogli nuovi, poi le flotte.

Sono dati pubblici, letti dal contratto, **costo zero**.

## Robinhood

La stessa decomposizione dà +19 punti dagli azzeramenti e +5 dai sopravvissuti. Ma su robinhood
l'effetto **non sopravvive** al controllo sulle apparizioni (vedi `VERDETTO_SOPRAVVIVENZA.md`):
quei numeri descrivono un effetto già sospetto, e non vanno usati come conferma.

## Il prossimo passo, dichiarato prima

Raccogliere gli attributi del contratto e del lanciatore, e misurare **sull'azzeramento come
bersaglio** invece che sul rendimento. Il bersaglio cambia: non «quanto rende» ma «va a zero sì
o no», che è una domanda binaria, più facile da misurare e con un fondale noto (31,5% su base).

E vale la stessa disciplina: metro misurato, nessuna soglia scelta dopo, e la ripetizione su
entrambe le chain.
