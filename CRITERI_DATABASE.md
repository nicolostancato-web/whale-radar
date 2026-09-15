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
| **1** | **Copertura per chain** (non aggregata) | ≥95% delle righe eleggibili, **in ciascuna chain** | base 96% ✅ · robinhood ~60% 🔴 · **solana 0%** 🔴 |
| **2** | **Solana esiste** | non dichiarabile sufficiente finché la copertura è «non iniziata» | 🔴 **non iniziata** |
| **3** | **Point-in-time provato** | ≥299 osservazioni **prospettiche** per strato chain/fonte, zero ritardi oltre l'embargo dichiarato | 🔴 **0** — il registro è nato ieri |
| **4** | **Backfill etichettato** | 100% dei record porta `acq` **e** la classe: `ricostruzione-storica` o `point-in-time-certificato`. Nessun record può essere marcato PIT solo perché oggi è recuperabile | 🟡 `acq` c'è, **la classe no** |
| **5** | **Integrità degli eventi** | audit indipendente su ≥299 finestre stratificate, zero discrepanze su evento canonico, pool, quantità grezze, ordinamento | 🔴 **mai fatto** |
| **6** | **Mappatura completa** | 100% dei record con chain, pool, **coppia di token**, block hash, id evento canonico, istante, **e semantica del wallet dichiarata**. I mancanti restano mancanti, non si inventano | 🔴 mancano coppia token, block hash, semantica del wallet |
| **7** | **Sopravvivenza** | ≥59 esclusioni campionate a caso con classificazione della causa, zero controesempi | 🔴 **17**, e non campionate a caso |

**Nessuna condizione è verde. Due sono gialle. Cinque sono rosse.**

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
