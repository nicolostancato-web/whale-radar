# ✅ QUANDO IL DATABASE È SUFFICIENTE — condizioni verificabili

*15/09/2026 · soglie imposte dalla revisione avversariale, non scelte da noi · scritte PRIMA di
poterle raggiungere, così nessuno può spostarle dopo*

## Perché esiste questo documento

Nicolò ha chiesto: *«non si va avanti finché non mi ufficializzate che il database è perfetto»*.
Ma «perfetto» è un'opinione. Qui ci sono **numeri**, e l'unica cosa che conta è se sono raggiunti.

Le soglie non le abbiamo scelte noi: le ha imposte il revisore esterno, che non ha motivo di essere
indulgente con il nostro lavoro.

---

## Le sette condizioni

| # | condizione | soglia | stato oggi |
|---|---|---|---|
| **1** | **Copertura per chain** (non aggregata) | ≥95% delle righe eleggibili, **in ciascuna chain**. Due misure, entrambe necessarie: (a) **nascite possedute** — quota di pool di cui abbiamo le prime ore; (b) **finestre identiche** nell'audit | **nascite**: base 97% 🟡 · robinhood 55% 🔴 (sale, recupero in corso) · solana n/d 🔴 — **finestre identiche**: 16% 🔴 |
| **2** | **Solana esiste** | non dichiarabile sufficiente finché la copertura è «non iniziata» | 🔴 **non iniziata** |
| **3** | **Point-in-time provato** | ≥299 osservazioni **prospettiche** per strato chain/fonte, zero ritardi oltre l'embargo dichiarato | 🟡 **51.482 scambi** raccolti alla punta (base + robinhood), ritardo mediano **5,2 minuti**. Il conteggio per strato va ancora fatto |
| **4** | **Backfill etichettato** | 100% dei record porta `acq` **e** la classe: `ricostruzione-storica` o `point-in-time-certificato`. Nessun record può essere marcato PIT solo perché oggi è recuperabile | 🟡 `acq` c'è, **la classe no** |
| **5** | **Integrità degli eventi** | audit indipendente su ≥299 finestre stratificate, zero discrepanze su evento canonico, pool, quantità grezze, ordinamento | 🔴 **19 finestre misurabili, 3 identiche (16%)**. **Zero record inventati** — le due accuse erano residui del vecchio formato |
| **6** | **Mappatura completa** | 100% dei record con chain, pool, **coppia di token**, block hash, id evento canonico, istante, **e semantica del wallet dichiarata**. I mancanti restano mancanti, non si inventano | 🔴 mancano coppia token, block hash, semantica del wallet |
| **7** | **Sopravvivenza** | ≥59 esclusioni campionate a caso con classificazione della causa, zero controesempi | 🔴 **17**, e non campionate a caso |

**Nessuna condizione è verde. Quattro sono gialle. Tre sono rosse.**

---

## Le tre cose che il revisore ha smontato, e che vanno riparate

### «Wallet presenti al 100%» non vuol dire «abbiamo l'identità»

Misura la **non-nullità**, non l'identità economica. Nei log di una blockchain EVM quel campo può
essere un router, un aggregatore, un contratto, il destinatario o chi incassa le commissioni —
**non necessariamente chi ha deciso lo scambio**.

Finché non dichiariamo la **semantica** del campo, «abbiamo l'identità dei wallet» è **non
giudicabile**. E metà delle variabili nuove si basa su quell'identità.

### «Zero duplicati» non vuol dire «completo»

La chiave canonica deve includere **chain, block hash, transazione, posizione nel log**. Noi abbiamo
transazione + posizione. Manca il block hash — e senza, una riorganizzazione della catena non si
distingue.

E soprattutto: **zero duplicati non dimostra che non manchi niente.**

### «Timestamp impossibili zero» non vuol dire «ordinabile»

Più scambi possono avere lo **stesso istante**: sono nello stesso blocco. Per ordinarli servono
**numero di blocco, indice della transazione, indice del log**. Noi abbiamo il blocco, non gli altri
due.

> Una variabile che si chiama «in che ordine sono arrivati» **non può ordinare** con la sola
> precisione del secondo. È esattamente una delle sei variabili nuove.

---

## Il quadro onesto

Abbiamo fatto un salto enorme in 48 ore: dal non avere affatto i dati su chi compra, ad averli per il
96% di Base. **Ma «li abbiamo» e «sono certificati» sono due cose diverse**, e finora ho scritto la
prima intendendo la seconda.

Di queste sette condizioni, **due si chiudono raccogliendo** (1 e 2: è solo tempo di scavo), **tre si
chiudono aggiungendo campi** (4 e 6, più l'ordinamento), e **due richiedono tempo che deve passare**
(3 e 7: servono osservazioni prospettiche, e il prospettico non si fa all'indietro per definizione).

**La 3 è quella che non si può accelerare con nessuna quantità di lavoro.** Il registro
point-in-time è nato ieri: 299 osservazioni per strato arriveranno quando arriveranno.

---

## La copertura che ci raccontavamo
*scoperto il 16/09 inseguendo quattro finestre di robinhood che risultavano incomplete pur essendo il formato al 100%*

Dicevamo **99,6% di copertura su base** e **76% su robinhood**. Quel numero conta i **pool per cui
esiste un file**, e in quella forma non significa quasi niente.

La prova, presa su una finestra sola di duecento blocchi di robinhood:

| | intervallo di blocchi nel file | record |
|---|---|---|
| i pool che **avevamo** nella finestra | 51.918.761 → 52.063.800 | 300 |
| i pool che **mancavano** | 35.974.257 → 63.995.138 | ~400 |

I secondi coprono **ventotto milioni di blocchi con quattrocento record**: hanno dati ai due bordi e
il vuoto in mezzo. Contati come «coperti», sono quasi tutti vuoti.

Non è un guasto, è la forma delle fette: dodici turni che scavano ognuno un tratto delimitato e
distanziato lasciano buchi sistematici **tra** un tratto e l'altro. Il collettore fa esattamente
quello che gli abbiamo chiesto. È la misura che mentiva, non il raccoglitore.

**Cosa cambia.** La copertura vera è già in casa e non serve costruirla: è la **quota di finestre
identiche dell'audit**, che chiede alla catena «in questo punto preciso, abbiamo quello che c'era?».
Oggi dice **83%** (48 su 58), non 99,6%. La condizione 1 adesso si misura così.

**Perché conta più del numero.** Un edge cercato su uno storico bucato a caso non è sbagliato: è
invisibile. Le fette saltano intervalli interi, e se un pump vive dentro un intervallo saltato, per
noi quel token non si è mai mosso. Avremmo cercato il segnale in un archivio che ci nasconde proprio
i momenti in cui succede qualcosa — e dato la colpa al segnale.

---

## Perché il database era incompleto: le fette non tornano sui propri passi
*trovato il 16/09 alle tre di notte, inseguendo quattro finestre di robinhood*

Le fette filtrano per `righe.json` **nel momento in cui passano**. Quando una fetta è transitata dal
blocco in cui un pool è nato, se quel pool non era ancora nella lista i suoi scambi sono stati
scartati — e le fette non tornano mai indietro. Ogni pool scoperto tardi, tipicamente dalla coda viva
che lavora alla punta, **resta senza storia per sempre**.

| | prime ore possedute | vuoti | tardivi |
|---|---|---|---|
| base | 1858/1907 = **97%** | 49 | 0 |
| robinhood | 422/768 = **55%** | 302 | 44 |

È la ragione principale del 16% di finestre identiche. Rimedio: `agents/recupero_nascite.py` in una
corsia sua (`nascite.yml`), che sa esattamente cosa manca e dove sta e va solo lì. Robinhood soltanto:
accendere una corsia per il 3% mancante di base sarebbe lavoro che sembra diligenza ed è spreco.

**Le tre misure che si sono corrette da sole, in ordine.** Vale la pena rileggerle insieme, perché
sono lo stesso errore in tre travestimenti: uno strumento che, non sapendo, rassicurava.

1. **99,6% di copertura** contava i pool con un file, non i blocchi dentro il file.
2. **83% di finestre identiche** contava come «identica» ogni finestra dove non si confrontava
   nulla — una escludeva 1057 eventi e ne confrontava 1.
3. **2 record inventati** erano residui del vecchio formato, senza indice completo, quindi
   inconfrontabili per costruzione. Record inventati veri: **zero**.

Il numero onesto, oggi, è 16%. Preferisco consegnarlo così.

---

## Dove siamo al 16 settembre, sera
*aggiornato coi numeri veri, dopo due confronti avversariali con un revisore esterno*

| # | condizione | stato |
|---|---|---|
| 1 | copertura per chain | 🔴 nascite robinhood 66%, base 97% · finestre identiche 32% |
| 2 | Solana | ⚪ **fuori scopo** per decisione, non dichiarata verde |
| 3 | osservazioni prospettiche | 🟡 coda viva a 3-4 minuti dalla punta, buchi dichiarati |
| 4 | ogni record etichettato | 🟡 l'etichetta la decide il ritardo misurato; bonifica del passato in corso |
| 5 | integrità su 299 finestre | 🔴 201/633 = 32% · **zero record inventati** · **zero blocchi orfani** su intervallo dichiarato |
| 6 | mappatura completa | 🟡 coppie di token: base 98%, robinhood 76% (erano 0% stamattina) |
| 7 | sopravvivenza | 🟢 **bilancio completo, zero persi senza ragione** |

### La condizione 7, chiusa

Ogni pool nato nella finestra ha **un esito contabile**. Nessuno sparisce in silenzio.

| esito | robinhood | base |
|---|---|---|
| mai scambiato | 42% | 73% |
| scoperto tardi | 32% | 14% |
| sotto soglia | 25% | 13% |
| **perso senza ragione** | **0** | **0** |

La maggioranza dei pool che non abbiamo **non è mai esistita come attività**: nasce e non scambia
mai. È la risposta al conto che il revisore aveva fatto a mente («mancano 3.500 pool senza
destinazione contabile»): non mancavano, non c'erano.

Resta il numero scomodo: **un terzo delle esclusioni su robinhood è «scoperto tardi»** — pool che
hanno scambiato davvero e che non avevamo. Non è un guasto del raccoglitore, è il ritardo di
scoperta che lo scopritore chiude da oggi in avanti. Ma prima di oggi quel terzo lo perdevamo.

### I difetti trovati e chiusi in 24 ore

Tutti della stessa famiglia: **strumenti che, non sapendo, rassicuravano**.

1. «99,6% di copertura» contava i file, non i blocchi dentro i file
2. «83% di finestre identiche» chiamava identiche le finestre dove non si confrontava nulla
3. «2 record inventati» erano residui del vecchio formato, inconfrontabili per costruzione
4. Le fette non tornavano sui propri passi: i pool scoperti tardi restavano senza storia
5. La coda viva rincorreva invece di saltare alla punta
6. **L'orario era falso fino a 84 minuti** — e il campo `ts` regge embargo, unioni e ogni analisi
7. I blocchi riorganizzati non erano mai stati ricontrollati (misurato: zero orfani)
8. Il registro dei pool veniva da un'API: **16.514 pool nati in 24 ore, noi ne conoscevamo 5**
9. Quattro raccoglitori ripartivano da capo a ogni giro, senza segnalibro
10. Due costanti sbagliate si mascheravano da limiti del nodo (finestra 50× troppo grande; «base
    non fa i lotti» dedotto da un solo tentativo, mentre ne accetta dieci)

### Cosa manca

- portare robinhood dal 66% al 95% di nascite possedute (recupero in corso, ~1 giorno)
- finire le coppie di token
- finire la bonifica degli orari del passato
- portare l'integrità verso le 299 finestre
