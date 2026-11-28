# Il tasso di diploma è sotto lo 0,3%, non l'8%

**11 ottobre, sera. Misura diretta, non un campione dei nostri archivi.**

## Come è stata fatta

Dal pomeriggio seguo le curve di Pons **dalla nascita**: ogni lancio letto dalla fabbrica, ogni
acquisto e ogni vendita, riserva netta aggiornata a ogni scambio. Nessun filtro, nessun registro
di mezzo.

| | |
|---|---|
| curve native seguite | **371** |
| seguite da almeno 1 ora | **306** |
| diplomi veri osservati | **0** |

E il tempo di diploma, misurato sulle 36 monete diplomate della prova post-diploma:
**30 su 36 si diplomano entro un'ora** dalla nascita della curva (mediana: minuti).

Quindi 306 curve hanno superato il tempo in cui si diploma l'83% di chi ce la fa. All'8% ci
sarebbero stati ~25 diplomi. **Zero.** Il tasso è sotto 1/371, cioè **sotto lo 0,3%**.

## Perché l'8% era sbagliato

Veniva dal 9 ottobre: avevo scoperto che `coppie.json` copriva 1 pool su 12 e avevo corretto il
tasso da 0,77% verso l'alto di dieci volte. **La direzione era giusta, la misura no**: contavo
come diplomi tutti i pool nuovi del gettone, e oggi ho scoperto che non lo sono.

Su **11 gettoni** che seguivo nella curva e che hanno avuto un pool nuovo, **11 su 11 avevano
hook zero**: pool creati da terzi, non diplomi di Pons. Un diploma vero ha l'hook
`0xe5e702641ea86f4ae6cc3cdaed2b886f976be044`, fee 0 e tickSpacing 200 — verificato su 3 diplomi
noti, riconosciuti 3 su 3.

**Chiunque può creare un pool per qualunque gettone.** Contare quei pool come diplomi gonfia il
tasso, e lo gonfiava di oltre dieci volte.

## Cosa cambia per la strategia

Il conto di stamattina — «su 100 allarmi a 3,6 ETH, 28 si diplomano» — era calcolato con la base
8%. Con una base sotto lo 0,3% quel 28% crolla, e con lui la soglia di pareggio che sembrava
generosa (perdere meno del 64%).

Resta vero quello che è misurato bene: entrando presto nel riempimento (1,5 nativi) le monete che
si diplomano rendono **3,08x** fino al diploma, e la prima perdita misurata su un fallimento è
**−69%**. Sono le due gambe del conto; quello che è cambiato è **quanto spesso** si incontra la
prima.

## La lezione, scritta in positivo

**Un tasso si misura seguendo le cose dalla nascita, non contando quante ne hanno un segno
dopo.** Ogni volta che ho contato «quante hanno X» su un archivio — i pool in `coppie.json`, i
pool nuovi di un gettone — ho sbagliato di un ordine di grandezza. Le due volte precedenti me
l'ha detto la cassaforte; questa volta me l'ha detto un esperimento che guarda in avanti.

E il segno va verificato: «ha un pool» non vuol dire «si è diplomata», come «ha un prezzo alto»
non voleva dire «l'abbiamo guadagnato».
