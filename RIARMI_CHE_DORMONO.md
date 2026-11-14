# I riarmi che dormono si mangiano metà della capacità

*1 ottobre 2026 · misurato sui 14 workflow che hanno un passo di riarmo*

## Il numero

| corsia | minuti a dormire per giro | orologio |
|---|---|---|
| piu_intelligente | 120 | una volta al giorno |
| iniziatori | 43 | ogni ora |
| hook | 41 | ogni ora |
| previsioni | 41 | ogni ora |
| riserve | 41 | ogni ora |
| scoperta | 41 | ogni ora |
| collector | 40 | ogni 2 ore |
| vivo | 37 | ogni ora |
| popolazione, riparazione, storico | 35 | ogni ora |
| insieme | 32 | ogni ora |
| censimento | 30 | ogni ora |
| soccorso | 23 | ogni ora |

**Totale: 622 minuti di macchina spesi a dormire, per un solo giro di ognuna.**

Le macchine gratis in parallelo sono venti, quindi un'ora di tempo disponibile vale 1.200
minuti-macchina. **I riarmi che dormono se ne mangiano il 52%.**

Una macchina che dorme occupa un posto esattamente come una che lavora.

## Perché è nato così, e perché è un cerchio

Il riarmo esiste perché **GitHub salta gli orologi sui repository occupati** (misurato il
25/09). Quindi ogni corsia, finito il lavoro, dorme mezz'ora e poi si rilancia da sola.

Ma è proprio quel dormire che tiene il repository occupato. **Il rimedio alimenta la malattia
che cura.** Ed è la spiegazione di tutto quello che ho rincorso oggi: giri che restano in coda,
giri annullati perché superati, corsie che sembrano morte e non lo sono.

## La prova del meccanismo, guardata dentro un giro

Il giro di `censimento` delle 19:17, visto lavoro per lavoro:

| lavoro | esito | durata |
|---|---|---|
| censisci (base) | **riuscito** | 2 min |
| censisci (robinhood) | **riuscito** | 2 min |
| riarmo | annullato | 10 min |

Il giro intero risulta **annullato**. Ma il lavoro era fatto in due minuti: l'unica cosa
annullata è il passo che **dormiva**.

Questo spiega anche perché per tre giri di fila ho creduto che `censimento` e `hook` fossero
morte e le ho rilanciate per niente: leggevo l'esito del giro invece dei lavori dentro il giro.
Lo stesso errore corretto oggi nelle guardie — e qui la sua causa.

## Perché non lo tocco stasera

Togliere il sonno senza togliere il rilancio fa girare le corsie **di continuo**: il sonno è
il distanziamento. Togliere il rilancio e tenere solo l'orologio è la mossa giusta — e oggi è
diventata possibile, perché la rete di guardie è stata riparata e proprio stasera ha rimesso
in moto quattro corsie davvero mute, senza rilanciarne una sola di sane.

Ma il 25 settembre ho propagato un miglioramento giusto a sei corsie in una volta e **ne ho
fatte cadere tre**, perché non avevo guardato l'effetto sul carico complessivo. Oggi ho già
pubblicato tredici correzioni. Quattordici corsie insieme, a quest'ora, è la stessa mossa.

**Come si fa invece:** si toglie il sonno a **due** corsie — `censimento` e `hook`, che hanno
un solo sonno e l'orologio ogni ora — si guarda per un paio d'ore se la rete di guardie le
tiene vive senza che girino di continuo, e **solo allora** si propaga alle altre dodici.

Se funziona, si liberano circa 600 minuti-macchina l'ora: più di quanto tutto il sistema
consumi oggi per lavorare davvero.
