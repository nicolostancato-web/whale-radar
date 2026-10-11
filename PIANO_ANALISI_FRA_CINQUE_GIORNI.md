# Le domande da fare al database, scritte prima di avere i dati — 9 ottobre 2026

La demo accumula con regola congelata: entrata a fine primo minuto, uscita al raddoppio, orizzonte
7 giorni, nessuno stop. Il database `cammino_posizioni.json` registra per ogni posizione minimi,
massimi, prezzo a orizzonti fissi e **la discesa peggiore prima del raddoppio**.

Queste sono le domande che gli farò fra cinque giorni. Sono scritte **adesso** perché l'errore di
questi giorni non è stato analizzare male: è stato decidere **cosa** analizzare dopo aver visto i
dati. Con cinquanta monete e la libertà di frugare, qualcosa torna sempre.

## Le cinque domande, in ordine

**1. Lo stop loss esiste?**
Quanto scendono le **vincenti** prima di raddoppiare, al peggio? Se nessuna scende sotto una certa
soglia, uno stop appena sotto è gratis: taglia le perdenti e non tocca le vincenti.
*Si risponde con: il minimo della discesa peggiore-prima-del-2x fra le vincenti, contro la
distribuzione delle perdenti nello stesso intervallo.*
Primo indizio su 3 casi: mediana −18%, ma **una è passata da −62%**. Se è la regola, lo stop al
−30% distrugge; se è l'eccezione, è gratis.

**2. L'uscita a tempo esiste?**
Fra le posizioni che **non** raddoppiano, a che punto è chiaro che non lo faranno? Se a un'ora chi
sta sotto 1,2x non raddoppia quasi mai, uscire lì libera capitale e taglia la perdita.
*Si risponde con: la probabilità di raddoppiare poi, condizionata al prezzo a 1h, 4h, 12h.*

**3. Il take profit al 100% è il migliore?**
Fra le vincenti, quante sarebbero andate oltre? Il massimo raggiunto dice quanto lasciamo sul
tavolo uscendo al raddoppio.
*Si risponde con: distribuzione del massimo fra quelle che toccano il 2x.*

**4. Entrare più tardi conviene?**
L'idea del pullback: il prezzo a 5 e 15 minuti contro quello d'entrata. Se chi poi raddoppia passa
quasi sempre da un calo iniziale, aspettare quel calo migliora l'entrata.
*Si risponde con: il prezzo a 5-15 min delle vincenti contro quello delle perdenti.*

**5. Quanto regge il capitale?**
Con la distribuzione vera e 10 euro per posizione su 100, quanti giri fa il capitale e quante
occasioni si perdono perché i soldi sono bloccati.
*Già misurato sullo storico: 175 occasioni perse su 283 e cassa finale 4,21 euro su 100. Da rifare
sui dati della demo.*

## Le regole dell'analisi, dichiarate adesso

- **si risponde a queste cinque domande e non ad altre.** Se ne nasce una nuova guardando i dati,
  si scrive, non si risponde: andrà provata su dati successivi;
- ogni numero esce con il suo **intervallo**; se contiene lo zero, «non dimostrato»;
- qualunque regola nuova che esca da qui **non si applica retroattivamente** alla demo in corso:
  la demo attuale resta la prova della regola congelata. Una regola nuova apre una **seconda**
  demo, con le sue date;
- soglia minima per guardare: **40 posizioni chiuse**, di cui almeno 15 non vincenti — altrimenti
  si guardano solo i sopravvissuti.

## Perché la precisazione sul compounding sta qui

Nicolò: *«anche qualcosa che ci dà in media un 50%, compounding, si fanno soldi.»* Vero **solo** se
la puntata è una frazione piccola del capitale. Con code grasse la media aritmetica e il risultato
composto divergono: una perdita del 95% cancella dieci vittorie da +100%, e reinvestendo tutto il
capitale il risultato composto può essere negativo con la media positiva.

Dieci euro su cento (un decimo per posizione) è la protezione giusta, ed è l'istinto che aveva
ragione. Con la distribuzione attuale — 40% a +100%, 60% a −95% — la media è **−17%**: per
arrivare a un 50% medio serve o che le perdenti perdano meno (domanda 1 e 2), o che le vincenti
corrano più del doppio (domanda 3). Sono le due sole leve, e il database misura entrambe.

---

## Domanda 8 (aggiunta il 10/10, nata dai dati stessi): l'orizzonte ci taglia i colpi grossi?

**Da dove viene.** Alla ventunesima chiusura, **tre monete su 27 hanno toccato il loro massimo
DOPO la nostra uscita**, e due erano vincenti che avevano già incassato il raddoppio:

| moneta | nostro esito | max vero | quando |
|---|---|---|---|
| `0x1f052479d2ff` | +90% (raddoppio) | **8,70x** | 1.208 min |
| `0xc65a7c91591a` | +90% (raddoppio) | **5,51x** | 1.136 min |
| `0xc3f40ab7a3b7` | −70% (orizzonte) | 8,28x | 1.258 min |

Il nostro orizzonte è 600.000 blocchi = **1.002 minuti (16,7 ore)**. Tutti e tre i massimi
cadono poco DOPO quella soglia. Non è una coincidenza sospetta: è una soglia che taglia proprio
dove il cammino diventa interessante.

**La misura.** Sulle sole posizioni chiuse, con il database del cammino che segue tutta la vita:

1. quante vincenti hanno un `max_x` oltre 2 volte il prezzo a cui siamo usciti;
2. la mediana di `max_dopo_minuti` per le vincenti, confrontata con 1.002;
3. il rendimento che avremmo avuto con orizzonte 24h, 48h e 7 giorni, a parità di regola
   d'uscita — **calcolato dal prezzo di entrata**, non dal prezzo iniziale (lezione del 24/09).

**Il cancello.** La terza misura va fatta su posizioni che hanno **già compiuto** sette giorni,
altrimenti si confronta un orizzonte lungo con monete che non hanno avuto il tempo di percorrerlo:
è la stessa asimmetria che fa sembrare brave le vincenti precoci. Oggi nessuna posizione ha sette
giorni, quindi questa domanda **non è ancora rispondibile**: va riaperta quando ce ne sono quindici.

**Perché non cambio niente ora.** Tre casi su 27 non distinguono un effetto da una coincidenza, e
allungare l'orizzonte adesso renderebbe le posizioni nuove non confrontabili con le vecchie —
perdendo il solo campione pulito che abbiamo.
