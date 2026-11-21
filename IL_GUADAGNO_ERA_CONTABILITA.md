# Le due misure concordano, e dicono 1,00X. Il guadagno era contabilita', non scambio.

*5 ottobre 2026 · riconciliazione operazione per operazione, come prescritto da Astra*

## Il numero che ritiro

Stamattina ho riferito: **31 operazioni al mese, 134$ di utile ciascuna, ~4.200$ al mese per
portafoglio copiato**. L'ho dato con entusiasmo. **E' sbagliato**, e questo documento spiega
esattamente come.

## La riconciliazione

Due misure della stessa operazione:

- **in dollari** — `incassato / speso`, dalle loro quantita';
- **al prezzo** — prezzo quando ha venduto / prezzo quando ha comprato, dalla pool.

| filtro sui gettoni venduti | n (robinhood) | dollari | prezzo |
|---|---|---|---|
| tutte | 945 | 1,29X | **1,00X** |
| venduto **>=99%** (il mio filtro) | 531 | **3,90X** | **1,00X** |
| venduto **fra 99% e 105%** | **15** | **1,01X** | **0,99X** |

Su base: 394 operazioni a 2,94X col mio filtro, **18** operazioni a **1,03X** col filtro giusto,
prezzo 1,00X in entrambi i casi.

**Dove il giro e' davvero chiuso, le due misure concordano e dicono 1,00X.**

## L'errore, nominato con precisione

Il mio filtro chiedeva «gettoni venduti **almeno** il 99% di quelli comprati». Ma quel rapporto
**puo' superare 1**: chi vende il 200% ha venduto gettoni che non abbiamo visto comprare in
quella pool. Nelle fasce basse la quota venduta mediana era **esattamente 200%**.

> **Una soglia «almeno» su un rapporto che puo' superare uno non e' un filtro: e' una porta
> aperta.** Serve una BANDA.

Quei gettoni in eccesso entrano nell'`incassato` senza un corrispondente `speso`, quindi il
multiplo in dollari sale per **costruzione contabile**. Il 3,90X non era un guadagno: era
l'assenza del costo di cio' che hanno venduto.

## Cosa resta vero, ed e' importante

1. **Il prezzo non si muove fra il loro ingresso e la loro uscita: 1,00X, in ogni fascia di
   costo, su entrambe le chain, a ogni ritardo.** E' la misura piu' solida di tutta la giornata,
   perche' non dipende da nessuna contabilita': confronta due prezzi della stessa pool.
2. **Quindi non c'e' niente da copiare in «compra quello che comprano, vendi quando vendono»:
   quel giro e' piatto.**
3. **Ma non dimostra che loro non guadagnino.** Guadagnano probabilmente **fuori da cio' che
   vediamo**: ricevono gettoni — dal lanciatore, da un altro indirizzo loro, da un gruppo — e
   li vendono. E' esattamente l'obiezione 4 di Astra: «state equiparando indirizzo, posizione e
   soggetto economico», e «un trasferimento ricevuto potrebbe essere avvenuto su un altro
   indirizzo dello stesso soggetto».

## Il limite di questa stessa misura, detto subito

**Solo 18 e 15 operazioni** passano il filtro stretto. E' poco, e lo e' per una ragione che
conta: **i giri davvero chiusi, comprati e venduti nella stessa pool nella stessa quantita',
sono rarissimi**. Quasi tutto cio' che vediamo e' entrata senza uscita, uscita senza entrata, o
quantita' che non tornano.

Quindi la conclusione corretta non e' «non guadagnano», ed e' piu' scomoda: **la maggior parte
di cio' che fanno non e' osservabile come uno scambio completo, e cio' che e' osservabile non
rende.**

## La conseguenza sul lavoro

L'ipotesi dei vincenti copiabili, nella forma «vedi cosa compra, compra anche tu», e' chiusa da
due misure indipendenti che concordano. Resta aperta nella forma che Nicolo' ha indicato:
**seguire la PERSONA e il suo finanziatore**, non la singola operazione — perche' se il
guadagno nasce da gettoni ricevuti, il segnale non e' l'acquisto, e' **chi riceve da chi**.
