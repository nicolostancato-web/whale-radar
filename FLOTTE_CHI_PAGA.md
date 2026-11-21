# Chi paga le flotte: milioni, non servizi

*2 ottobre 2026 · 73 portafogli risolti, 5 flotte, i tre finanziatori più grandi verificati*

## Il controllo di validità che poteva demolire tutto

Trovate cinque flotte — portafogli nuovi finanziati dalla stessa mano, con importi identici e
tondi. Ma un prelievo da **exchange** è anche lui di importo tondo, e se il finanziatore comune
fosse un servizio che finanzia tutti, «stessa mano» non significherebbe niente.

La domanda giusta: **quante transazioni ha fatto in tutta la vita quel finanziatore?** Un
exchange o un bridge ne ha centinaia di migliaia. Una persona ne ha poche centinaia.

## La risposta

| finanziatore | portafogli finanziati | transazioni totali | saldo |
|---|---|---|---|
| `0x0d0707963952f2fb…` | 9 | **65** | **$5.641.441** |
| `0x3304e22ddaa22bcd…` | 8 | **371** | **$62.943.647** |
| `0xbaed383ede0e5d9d…` | 5 | **172** | **$23.612.338** |
| `0x186c4a3c7da25e05…` | 4 | 0 | $0 |
| `0x97b9d2102a9a65a2…` | 4 | 0 | $2 |

**Non sono servizi.** Sessantacinque operazioni in vita e cinque milioni e mezzo in cassa è il
profilo di una mano singola con molti soldi — e nove di quelle operazioni sono state finanziare
nove portafogli nuovi che hanno comprato monete appena nate.

Il primo non ha log né transazione di creazione: è un indirizzo normale, non un contratto.

## Cosa resta inspiegato, e non lo nascondo

Gli ultimi due riportano **zero transazioni e saldo zero**. Un indirizzo con zero transazioni non
può aver finanziato quattro portafogli: o il contatore dell'esploratore non conta quel tipo di
movimento (transazioni interne da un contratto), o quei quattro collegamenti sono sbagliati.
**Va capito prima di contarli**, e fino ad allora le flotte solide sono tre, non cinque.

## Cosa questo stabilisce, e cosa no

**Stabilito:** esistono entità ricche che creano e finanziano flotte di portafogli nuovi, e
quei portafogli comprano memecoin appena nate. La struttura che Nicolò descriveva da mesi
**esiste e si misura**, a costo zero, con dati pubblici.

**Non stabilito:** che seguirle faccia guadagnare. Il legame con gli esiti è appeso a **cinque
pool**.

### La mia spiegazione di quel cinque era sbagliata, e il test l'ha detto subito

Avevo scritto che conoscevamo solo i primi dieci compratori e che «le flotte comprano nella
scia», quindi alzando il tetto a quaranta i pool misurabili sarebbero diventati centinaia.
Alzato: la mediana dei compratori conosciuti per pool è passata a 12 e il massimo a 40, e i pool
toccati da una flotta sono passati da **cinque a SEI**.

**Le flotte non stanno fra l'undicesimo e il quarantesimo compratore. Non sono lì.**

Il motivo vero era più semplice e l'avevo sotto gli occhi: **73 portafogli risolti su 11.275**.
Settantatré indirizzi non possono toccare più di una manciata di pool giudicabili, qualunque sia
la profondità con cui li si cerca. Non era un problema di *dove* guardavo: era di *quanti*.

Lezione, la stessa della notte in altra forma: **prima di spiegare un numero piccolo con un
meccanismo, controllare se è piccolo perché il denominatore è piccolo.**

### Il percorso critico, con i numeri

Al ritmo attuale — quota del servizio pubblico, ~40 portafogli per giro — mille portafogli
richiedono venticinque giri, circa un giorno. Con una **chiave gratuita di Etherscan**
(registrazione senza carta, 5 chiamate al secondo, 100.000 al giorno) tutti gli 11.275 si
risolvono in **meno di un'ora**, e il legame flotte→esiti diventa misurabile stasera invece che
domani. La corsia è già pronta a usarla: se trova `ETHERSCAN_KEY` fra i segreti passa a quella
strada da sola.

**E il limite che non cambia:** solo base. Robinhood non ha un esploratore pubblico che
risponda, quindi la regola di ripetizione non può essere soddisfatta. Qualunque cosa esca da qui
è un **indizio forte**, non una strategia da mettere in produzione.
