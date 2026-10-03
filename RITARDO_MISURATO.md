# ⏱️ IL RITARDO VERO, MISURATO — condizione 3

*15/09/2026 · primo risultato del timbro di acquisizione · 149.620 record*

## Cosa misura

Il timbro `acq` dice **quando un dato è entrato da noi**. Confrontato con `ts` — quando il fatto è
avvenuto — dà il ritardo reale, record per record. È la misura che il revisore chiedeva, e che prima
di ieri era **impossibile**: il nostro GC aveva schiacciato la storia git l'11 settembre.

## I numeri

| chain | fonte | record | mediana | p90 | p99 |
|---|---|---|---|---|---|
| base | **fornitore** | 2.196 | **0,9 h** | 11,0 h | **12,6 h** |
| robinhood | **fornitore** | 780 | **3,6 h** | 4,0 h | **4,4 h** |
| base | catena (backfill) | 97.164 | 362 h | 596 h | 890 h |
| robinhood | catena (backfill) | 49.480 | 614 h | 782 h | 819 h |

## Due conclusioni, opposte

### 1. Il ritardo dei fornitori sugli SCAMBI è molto più basso di quanto credevamo

Usavamo 10,8 ore per Base — ma quel numero era misurato **sulle candele**. Sugli scambi la mediana
reale è **0,9 ore**, e il 99% arriva entro **12,6 ore**.

Non cambia l'embargo da solo: un embargo va scelto su un percentile alto, non sulla mediana. Ma
adesso il numero **è misurato** invece che ereditato da un'altra grandezza.

### 2. Il backfill dalla catena NON può essere certificato point-in-time, e il timbro lo dimostra

Mediana **362 ore** su Base, **614** su Robinhood. Ovvio, per costruzione: stiamo raccogliendo adesso
la storia di token nati settimane fa.

> Il revisore l'aveva detto: *«`acq` prova che quei dati sono entrati adesso; per quei record prova
> il contrario di quello che vorresti»*. **Adesso c'è il numero che lo conferma.**

È il motivo per cui ogni record di backfill porta scritto `classe: ricostruzione-storica`. Non è una
formalità: è la differenza fra un dato su cui si può esplorare e un dato su cui si può decidere.

## Cosa significa per il progetto

Abbiamo **due database**, e vanno tenuti distinti per sempre:

| | cos'è | a cosa serve |
|---|---|---|
| **ricostruzione storica** | 147.000 record, raccolti all'indietro | **esplorare**: cercare quali variabili sembrano avere senso |
| **certificato point-in-time** | quello che raccogliamo **da adesso in avanti**, col timbro | **decidere**: l'unico su cui un verdetto vale |

Il primo è grande e disponibile subito. Il secondo cresce un giorno alla volta e **non si può
accelerare in nessun modo** — è il vincolo vero del progetto, e nessuna quantità di lavoro lo sposta.

## Cosa manca per chiudere la condizione 3

Servono **299 osservazioni prospettiche per strato** (chain × fonte) con ritardo entro l'embargo
dichiarato. Oggi:

| strato | record col timbro | serve |
|---|---|---|
| base / fornitore | 2.196 | ✅ abbastanza |
| robinhood / fornitore | 780 | ✅ abbastanza |
| base / catena in avanti | **0** | 🔴 comincia adesso |
| robinhood / catena in avanti | **0** | 🔴 comincia adesso |

I primi due strati **superano già la soglia**. Gli ultimi due partono da zero oggi: sono i dati che
raccoglieremo sui pool **appena nati**, scansionati subito invece che a settimane di distanza.
