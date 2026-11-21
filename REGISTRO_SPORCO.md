# Un quarto del registro robinhood non e' fatto di pool

Inseguendo i 350 «pool registrati e mai letti» ho trovato una cosa diversa da quella che cercavo,
e piu' seria: **buona parte di quelle voci non sono pool.**

## La verifica

Per ogni indirizzo mai letto ho chiesto al nodo, **su tutta la chain e senza finestra**: hai mai
emesso un log di swap? Non «nella finestra che stimo io» — mai, dal blocco zero a oggi. Un pool
che ha scambiato una volta sola in vita sua risponde di si'.

| | voci mai lette | **mai scambiato in tutta la chain** | ha scambiato (buco vero) | illeggibili |
|---|---:|---:|---:|---:|
| robinhood | 204 | **203** | 0 | 1 |
| base (indirizzi) | 44 | — | — | 44 |

Su base il nodo rifiuta le domande a tutta altezza, quindi **base resta non misurata**: non e'
«base e' pulita», e' «non l'ho ancora chiesto in un modo che base accetti». Va fatto a finestre.

Gruppo di controllo, per sapere se la domanda funziona: 15 pool che invece leggiamo. I 3 leggibili
hanno tutti risposto «si', ho scambiato». La domanda funziona.

E interrogando quei contratti: **9 su 10 non sono ne' pool ne' token** — non rispondono a `token0()`
ne' a `symbol()`. Uno era un token ERC20 (`DLMM`) iscritto fra i pool.

## Perche' e' piu' seria di un buco

Un buco toglie righe. Una voce falsa nel registro **gonfia il denominatore di ogni percentuale che
abbiamo pubblicato su robinhood** — e le fa sembrare peggiori di come sono, nascondendo dove sta il
lavoro vero.

| misura | come l'ho riportata | sul registro vero |
|---|---:|---:|
| nascite risolte dalla catena, robinhood | 506/797 = **63%** | 506/593 = **85%** |

Per settimane ho scritto che robinhood era indietro su base (84%) sulle nascite. **Non lo era.**
Erano 204 voci che non potevano avere una nascita perche' non erano pool: nessun evento da
risolvere, iscritte per sempre nella colonna «da fare».

E' lo stesso difetto per cui il consulente mi ha corretto sull'integrita' ieri — misurare una
popolazione che il processo stesso ha scelto — solo dall'altro lato: li' il denominatore si
restringeva e la percentuale saliva; qui il denominatore si gonfia e la percentuale scende. In
entrambi i casi il numero parlava del nostro processo, non della chain.

## Cosa ho fatto e cosa no

**Non le ho cancellate.** Sono in `data/quarantena_registro.json` con l'esito della verifica per
ognuna. Cancellare e' irreversibile e non serve: basta che chi calcola una percentuale sappia
quali voci escludere, e il file glielo dice.

**Resta aperto:** la stessa verifica su base, a finestre, e i 102 id V4 di base mai letti — quelli
hanno nascita dalla catena e nel campione **7 su 12 avevano scambi**, quindi li' il buco e' vero
e va colmato.
