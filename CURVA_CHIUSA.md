# La curva è chiusa — verdetto del 6 ottobre 2026

## Tutto quello che si può fare, in una tabella

| strategia | operazioni | risultato | eseguibile? |
|---|---|---|---|
| comprare a caso | 524.717 | 0,4610x | sì |
| evitare le curve con puntate iniziali grosse | 50.333 | **0,6227x** | sì |
| copiare chi ha già guadagnato | 3.672 | **1,0609x** | **no** |
| copiare, con mezzo secondo di margine | 1.248 | 0,9619x | sì |
| copiare + margine + puntate piccole | 291 | 0,9444x | sì |

**Nessuna strategia eseguibile supera 1.** Il meglio è 0,96x: si perde il 4%.

## I due segnali veri, che però non bastano

**1. Esistono operatori sistematicamente migliori.** 181 su 1.285 guadagnano in entrambe le metà
della propria storia, contro un massimo di 24 che il caso spiega — su un metro che passa il
criterio di validità fissato prima (scarto fra mediane 0,012 < 0,03). Sette metri costruiti, sei
buttati.

**Ma il loro vantaggio è di esecuzione, non di analisi**: il margine mediano per entrare dopo di
loro è **0,3 secondi**, e il 31,4% degli acquisti consecutivi è nello stesso blocco. Appena
chiediamo mezzo secondo, il rendimento scende da 1,09x a 0,96x.

**2. Le puntate iniziali grosse predicono il disastro.** Monotono su cinque fasce e 580.000
operazioni:

| puntata media nei primi 20 secondi | ritorno di chi compra dopo |
|---|---|
| la più piccola | **0,6577x** |
| la più grande | **0,2406x** |

Non conta **quanta gente** arriva (piatto: 0,43 contro 0,45), conta **quanto grosse sono le
puntate**. Quando i primi mettono cifre grosse, sono loro che scaricheranno su chi viene dopo.

Dimezza la perdita. **Non la ribalta.** E combinato con la selezione dei portafogli peggiora
(0,9444x contro 0,9619x): i due segnali non si sommano.

## Perché chiudo questa strada

Non per mancanza di segnale — il segnale c'è ed è misurato due volte. Perché **il segnale vive
dove non possiamo arrivare**, e quello che possiamo raggiungere perde il 4%.

Continuare vorrebbe dire costruire infrastruttura di esecuzione sub-secondo, che è un altro
mestiere e un'altra scala di investimento.

## Le tre strade che restano, in ordine di promessa

1. **Il mercato pubblico delle monete che graduano** (lo 0,8%). Lì la tenuta mediana è di **5,5
   ore**, non di decimi di secondo: la velocità conta molto meno. È il posto naturale dove portare
   tutto quello che abbiamo imparato stanotte.
2. **I 451 che comprano e non vendono mai.** Comprano 50-130 monete e non ne liquidano nessuna
   pur potendo (verificato sulla chain: zero vendite mancanti). È l'unico comportamento della
   giornata senza spiegazione.
3. **L'altro 50%**, parcheggiato: Grok ci sta lavorando, 3 domande su 10 fatte, tutte e tre con
   esito «porta chiusa» documentato.

## Cosa portiamo via, che vale più del verdetto

- un metro validato (`agents/metro_dei_bravi.py`) che **si rifiuta di scrivere un verdetto** se
  non passa il criterio di validità;
- il costo di copiare, misurato e non stimato: **2%**;
- il margine di esecuzione, misurato: **0,3 secondi mediani**;
- e sette controlli che, oggi, hanno ucciso sei risultati entusiasmanti — quattro dopo averli
  pubblicati, **tre prima**.
