# 🚨 LA NASCITA CHE USAVAMO ERA SBAGLIATA DI VENTI ORE

*17 settembre 2026, 03:00 · il difetto più grave trovato finora nel database*

## Il fatto, misurato su 142 pool

Tutto il database usa come «nascita» di un pool il primo istante delle sue **candele**. Ma le
candele cominciano quando GeckoTerminal **si accorge** del pool, non quando il pool nasce.

Confrontando con l'evento `Initialize` della catena — che dice l'istante esatto:

| | |
|---|---|
| pool misurati | **142** |
| errore mediano delle candele | **+20,46 ore** |
| **pool il cui errore supera la finestra di 6 ore** | **109 su 142 = 77%** |

## Cosa significa

Noi teniamo «**le prime 6 ore di vita**» di ogni pool. Se l'istante di partenza è in ritardo di
venti ore, quella finestra è spostata in avanti di venti ore: **per il 77% dei pool, quelle che
abbiamo raccolto e chiamato "prime sei ore" non si sovrappongono nemmeno alle prime sei ore vere.**

Non è un dato impreciso. È il dato di un altro periodo.

## Cosa contagia

Tutto ciò che usa la nascita da candele, cioè quasi tutto:

- **il recupero nascite** — cercava ogni pool nel posto sbagliato: 16.837 chiamate, zero raccolto
- **l'audit di integrità** — il filtro «dentro le prime ore» decide cosa confrontare
- **la classificazione delle esclusioni** (condizione 7) — «mai scambiato» può voler dire
  «non ha scambiato nella finestra sbagliata che gli abbiamo guardato»
- **la misura «nascite possedute»** — il 97% di base e il 66% di robinhood
- **la selezione stessa dei pool giovani**

## Come è saltato fuori

Inseguendo un sintomo apparentemente banale: il recupero nascite faceva migliaia di chiamate e
raccoglieva zero. Tre difetti veri corretti lungo la strada — chiave del segnalibro mobile, dati
scartati mentre li guardavo, istante interpolato invece che chiesto — e **nessuno dei tre era la
causa**. La causa era che stavamo cercando nel posto sbagliato dall'inizio.

Una sonda mirata l'ha inchiodato: 99 scambi di pool cercati, firma perfetta, tutti «fuori
finestra». Non erano fuori: era la finestra a essere nel posto sbagliato.

## Il rimedio

`agents/nascita_vera.py` chiede alla catena l'istante esatto di creazione di ogni pool V4, con una
sola chiamata per pool (il filtro `Initialize` + id è così selettivo che copre l'intera catena in
una volta). Ogni nascita porta scritto **da dove viene**: `catena` quando è l'istante vero,
`candele` quando è ancora una stima.

Per i pool con indirizzo (V2/V3) l'evento equivalente va ancora trovato: per quelli resta la
candela, **dichiarata come stima**.

## La lezione, che è la stessa di due giorni

Un dato che non dice da dove viene costringe chi lo usa a fidarsi. Abbiamo passato due giorni a
inseguire numeri che sembravano sensati — 99,6% di copertura, 83% di finestre identiche, zero
record inventati, 97% di nascite possedute — e ogni volta il numero misurava qualcosa di diverso
da quello che il suo nome diceva.

**Questa volta il numero era giusto e sbagliato era il momento in cui guardavamo.**

---

## ⚠️ CORREZIONE (17/09, poche ore dopo): il difetto è di robinhood, non di tutti

Avevo scritto che il difetto «contagia quasi tutto». **Era un'estrapolazione da sei pool di
robinhood, ed era troppo larga.** Misurato su entrambe le chain:

| chain | pool misurati | errore mediano delle candele | oltre la finestra di 6 ore |
|---|---|---|---|
| **base** | 219 | **+0,00 ore** | 21 (**10%**) |
| **robinhood** | 83-165 | **+16 / +38 ore** | **77%** |

**Le candele di base sono accurate.** GeckoTerminal indicizza bene una chain matura e arriva tardi
su robinhood, che è nuova. Quindi:

- **base** (1.919 pool, il grosso del database): largamente sano
- **robinhood** (785 pool): compromesso, e lì la nascita va presa dalla catena

Il rimedio resta lo stesso e vale per entrambe — la nascita vera dalla catena è comunque più
affidabile di una stima — ma **l'urgenza è su robinhood soltanto**, e le conclusioni tratte su base
non vanno buttate.

### Una nota su come sono arrivato a sbagliare

Sei pool, tutti della stessa chain, e ho scritto «contagia quasi tutto». È lo stesso errore che
questo progetto ha già fatto tre volte in due giorni: **prendere una misura fatta su una parte e
parlarne come se valesse per l'insieme.** Il 99,6% di copertura, l'83% di finestre identiche, il
97% di nascite possedute — tutti numeri veri su una popolazione e falsi sull'universo.

Stavolta l'ho fatto nella direzione opposta, allarmandomi troppo invece che troppo poco. È lo
stesso difetto.
