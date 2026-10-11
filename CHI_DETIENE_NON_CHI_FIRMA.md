# Il cancello boccia 10 su 10 — ma forse sta guardando l'indirizzo sbagliato

*6 ottobre 2026 · lo stato onesto, con un test ancora aperto*

## Cosa ho verificato, e regge

| cosa | esito |
|---|---|
| mappa **pool → gettone** | **CORRETTA**: una pool si chiama letteralmente `UniswapV3Pool` e contiene i nostri due lati |
| attribuzione **transazione → firmatario** | **CORRETTA**: 3 su 3 e 6 su 6 coincidono con la chain |
| esclusione degli arbitraggi atomici | funziona: da 1.386-2.486 a **10.746-14.066** per fetta |

## Cosa boccia

Il cancello, sul campione a caso dai dati corretti: **10 casi su 10 FALSI** — peggio del
4-su-6 di prima. Nessuno dei portafogli risulta aver toccato il gettone che gli attribuiamo.

## E qui il fatto nuovo, che rimette in discussione il cancello e non i dati

Aprendo gli scambi di una pool verificata, il campo che registriamo come destinatario (`w`)
e' un **TERZO indirizzo** — ne' il firmatario, ne' il router:

```
transazione  0x80c8ccbc…
  firmatario (chi decide, e chi usiamo noi)   0x048ef106…   EOA, non contratto
  destinatario dello scambio (w)              0x8f10b468…   un altro indirizzo
```

E in altri scambi della stessa pool il destinatario era il **router universale di Uniswap**
(`0x262666…`), mentre il firmatario cambiava a ogni transazione.

**La struttura e': un portafoglio firma, e i gettoni finiscono in un indirizzo diverso** —
un router, o un contratto proprio di quel bot.

**Conseguenza sul mio controllo:** cerco i trasferimenti del gettone **nel firmatario**, che
non lo tiene MAI. Zero trasferimenti e' quindi il risultato ATTESO, e non dice niente su
quanto abbia guadagnato quel portafoglio.

**Non sto dicendo che i dati sono giusti.** Sto dicendo che **il verdetto del cancello non e'
piu' interpretabile**: boccia sia i dati sbagliati sia quelli giusti, quindi non distingue.
Un controllo che boccia tutto non e' severo, e' rotto — ed e' la stessa famiglia del controllo
che «guardava la fonte sbagliata» (1/10) e di quello che «leggeva la menzione invece
dell'esecuzione» (4/10).

## Il test che lo decide, e perche' non l'ho chiuso

Basta chiedere: **il destinatario `w` detiene quel gettone?** Se si', il guadagno e' reale e
il mio controllo andava cambiato; se no, il difetto e' nei dati.
Non l'ho chiuso perche' dopo centinaia di chiamate stanotte l'esploratore ci strozza: il
firmatario risponde (zero trasferimenti, come previsto), il destinatario va in timeout.
Si riprende con pazienza, non con piu' chiamate.

## Cosa NON faccio

Non riporto nessun numero, e non dichiaro i dati veritieri. La regola di Nicolo' resta in
piedi: due sole risposte possibili, e oggi la risposta e' **«sto ancora lavorando»**.
Ma aggiungo l'onesta' che serve: **non so ancora se il problema sia nei dati o nel mio modo di
verificarli**, e finche' non lo so non posso nemmeno dire quanto siamo lontani.
