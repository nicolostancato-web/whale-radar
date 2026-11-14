# Un dubbio alla base: cos'è la «famiglia 4»? — 7 ottobre 2026

## Mi fermo, e spiego perché

Costruendo la misura sul mercato pubblico ho trovato un'incoerenza che sta **sotto** diversi
risultati di ieri. Non la aggiro: la nomino e la risolvo prima di andare avanti.

## I fatti, misurati adesso

**1. Il registro dei pool contiene due famiglie diverse:**

| famiglia `dex` | voci | forma dell'identificativo |
|---|---|---|
| **4** | **57.141** | id da **64 cifre** (non è un indirizzo) |
| 23 | 12.998 | indirizzo normale da 40 cifre |

**2. Sulla chain non esiste un solo scambio Uniswap v4.** Cercato con la firma
`0x40e9cecb9f5f1f1c5b…` — che **coincide esattamente** con la costante `SWAP_V4` del nostro
collettore, quindi la firma è giusta — in tre finestre diverse (recenti e storiche): **zero
risultati** ogni volta.

**3. I trasferimenti di una moneta «graduata» vanno alla sua curva.** Sulla moneta
`0xc293e1b1…`, la controparte più frequente dei 386 trasferimenti è
`0xd94f90f82636a8…`, che è **la curva di Pons di quella stessa moneta**.

**4. E la stessa moneta, nel registro, ha ZERO pool.** Quindi la funzione che la classificava come
«graduata» stava usando una versione diversa del registro, oppure la classificazione è sbagliata.

## Che cosa questo mette in dubbio

Se la famiglia 4 non è Uniswap v4 ma qualcos'altro — plausibilmente le coppie interne della curva
stessa — allora «la moneta ha un pool» non significa «la moneta è arrivata al mercato pubblico». E
cadono:

- **lo 0,8% di graduazione** (5.169 o 11.489 o 12.970 secondo la versione del registro: già il
  fatto che il numero balli di due volte era un segnale che non ho raccolto);
- la separazione fra «morta sulla curva» e «graduata», e quindi il confronto fra le due;
- il «77,5% di chi risultava mai venduto ha mosso gettoni nel mercato pubblico» — se quel mercato
  è la curva, non ha mosso niente di nuovo.

## Che cosa NON mette in dubbio

- il verdetto sulla curva (**nessuna strategia eseguibile supera 1**): è costruito solo su
  `CurveBuy`/`CurveSell`, eventi verificati sulla chain con il keccak, e non usa il registro dei
  pool;
- il metro validato e i 181 operatori contro 24 del caso: stessa ragione;
- il margine di esecuzione di **0,3 secondi** e il costo di copiare del **2%**: misurati sulla
  fila degli acquisti alla curva.

## Il segnale che avevo sotto gli occhi e non ho raccolto

Il numero delle monete graduate è cambiato tre volte in un giorno: **5.169 → 11.489 → 12.970**.
L'ho attribuito ogni volta a «il registro in cielo è più fresco del mio», che era comodo e
plausibile. Ma **un numero fondamentale che raddoppia merita una domanda, non una spiegazione.**

È la famiglia di errore che questo progetto ha già nominato: *la spiegazione che salva l'ipotesi è
la prima che viene in mente, e va sospettata per default.*

## Il prossimo passo, uno solo

**Capire cos'è la famiglia 4 su robinhood**, chiedendolo alla chain e non a me stesso: prendere un
id da 64 cifre, trovare quale contratto emette i suoi eventi, e leggere che cosa è. Da quella
risposta dipende se «graduata» significa qualcosa.

Finché non ce l'ho, non costruisco altro sul mercato pubblico.
