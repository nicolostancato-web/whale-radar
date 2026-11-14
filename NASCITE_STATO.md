# 📍 LE NASCITE — da dove viene la data di nascita di ogni pool

*17 settembre 2026 · aggiornato dopo due giorni di correzioni*

## Perché conta

Teniamo **le prime sei ore di vita** di ogni pool. Se la data di nascita è sbagliata, quella
finestra è spostata: raccogliamo sei ore di un altro momento, e ci costruiamo sopra l'audit di
integrità, la classificazione delle esclusioni e la misura di copertura.

## Le quattro situazioni, misurate

| chain | tipo di pool | fonte della nascita | errore delle candele | stato |
|---|---|---|---|---|
| **base** | V4 (id) | evento `Initialize` sulla catena | **+0,0 ore** | ✅ risolto, 83% |
| **base** | indirizzo | **candela** | non misurato | ⚠️ vedi sotto |
| **robinhood** | V4 (id) | evento `Initialize` sulla catena | **+16 ore**, 77% fuori finestra | ✅ risolto |
| **robinhood** | indirizzo | primo scambio sulla catena | **+114 ore** (5 giorni) | 🔄 in corso, ~50% |

## La decisione presa oggi sui pool con indirizzo di base

**Restano sulla candela, e lo dichiariamo.** Sono ~300 pool su 1934, il 15% di base.

Perché non li risolviamo: il nodo pubblico di base obbliga a tratti da 4.000 blocchi con filtro per
indirizzo. Per coprire settimane di storia servirebbero migliaia di chiamate **per pool** — giorni
di lavoro per il 15% di una chain le cui candele, sui 219 pool V4 misurati, sbagliano di **zero
ore**.

**Cosa sappiamo e cosa assumiamo**, tenuti separati:
- *sappiamo*: su base le candele dei pool V4 sono esatte (+0,0h mediane, 219 casi)
- *assumiamo*: che lo siano anche per i pool con indirizzo della stessa chain
- *non sappiamo*: se l'assunzione regge, perché non l'abbiamo verificata

L'assunzione è ragionevole — è la stessa fonte che indicizza la stessa chain — ma **è
un'assunzione**, e su questo progetto le assunzioni ragionevoli si sono rivelate false tre volte in
due giorni. Quindi sta scritta qui invece che sepolta nel codice.

## Come si riconosce una nascita affidabile

Ogni record porta il campo `fonte`:

| valore | significato |
|---|---|
| `catena` | istante vero, preso dall'evento di creazione o dal primo scambio confermato |
| `catena-non-confermata` | il cammino all'indietro si è **troncato**: è il bordo della ricerca, non la nascita |
| `candela` | stima da GeckoTerminal |

**Solo `catena` entra nelle statistiche.** Un cammino troncato non è una nascita: è il punto in cui
abbiamo smesso di guardare — lo stesso difetto della candela, in versione nostra.

## I quattro errori corretti per arrivare qui

1. **La candela non è la nascita**: GeckoTerminal registra quando *si accorge* del pool
2. **Il cammino troncato contato come nascita**: 54 su 64 erano il bordo della ricerca
3. **Il passo fisso non arrivava mai in fondo**: 100.000 blocchi alla volta sono 67 ore su
   robinhood; raddoppiando, dieci chiamate coprono cento milioni di blocchi
4. **Un pezzo senza limite affamava gli altri**: la scansione dei V4 su base consumava tutto il
   budget e la sezione degli indirizzi non veniva mai raggiunta — zero tentativi, in silenzio
