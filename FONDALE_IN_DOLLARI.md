# Il fondale, finalmente in dollari — e la direzione si chiude per davvero

*29 settembre 2026, notte. Primo numero prodotto simulando di VENDERE, invece di applicare una
convenzione. Nessun euro rischiato.*

## Come è stato ottenuto

Fino a ieri il fondale dipendeva da una regola scritta da noi — *«meno di cinque vendite = hai perso
tutto»* — che da sola valeva **55 punti** (misurato in H8). Una scelta, non una misura, nel posto in
cui si decide il verdetto.

Ora si simula: si prende il flusso vero delle vendite dopo l'entrata, in ordine di tempo, e ci si
prova a piazzare dentro una posizione da 100, 500 o 2000 dollari, prendendo i prezzi come arrivano.
**Quello che non si riesce a vendere entro 24 ore vale zero.**

## Il risultato

**robinhood — 6.056 mercati giudicabili**

| posizione | riempita del | media | senza l'1% alto | mediana | sotto −90% |
|---|---|---|---|---|---|
| **$100** | 100% | −21,7% | −25,5% | −4,3% | 14,8% |
| **$500** | **77%** | −39,0% | −42,2% | −29,8% | 27,8% |
| **$2000** | **19%** | −56,6% | −59,3% | −82,1% | 42,9% |

**base — 2.616 mercati** (peggio in ogni riga)

| posizione | riempita del | media | mediana |
|---|---|---|---|
| $100 | 100% | −35,5% | −4,2% |
| $500 | 32% | −51,6% | −68,5% |
| $2000 | 8% | −67,1% | −93,4% |

## Cosa dice, in una frase

**Non è che ci manchi un filtro: il mercato non regge i soldi.**

Con cento dollari si esce sempre, e si perde il 22%. Con cinquecento **esce solo il 77% della
posizione**. Con duemila, il 19% — cioè quattro quinti dei soldi restano dentro e valgono zero.

Il fondale non è un numero: **è una curva che peggia con la taglia**, ed è la ragione per cui ogni
strategia provata su questi mercati era condannata prima di cominciare. Nessuna regola d'ingresso
può risolvere un mercato che non ti fa uscire.

## Perché questo numero è credibile, a differenza dei precedenti

- non seleziona i pool: compra **tutti** quelli giudicabili, e misura cosa succede;
- non usa nessuna soglia arbitraria: **simula**;
- non condiziona su niente che si conosca dopo l'entrata per SCEGLIERE (solo per misurare l'esito);
- gira sugli strumenti riparati questa settimana — verso, finestra, criterio di scarto, taglia —
  ognuno con un guasto storico nel banco che lo verifica a ogni pubblicazione.

## Cosa comporta

**Questa direzione è chiusa, e stavolta per una ragione fisica invece che statistica.** Prima
dicevamo «il premio è troppo piccolo»; adesso sappiamo che **il premio non è incassabile**.

Ne segue anche un criterio per la prossima direzione, che vale più del verdetto:

> **Prima di studiare se un mercato sale, misurare se ci si può uscire con i soldi che vogliamo
> metterci.** È una domanda che si risponde in un'ora e che avrebbe risparmiato nove strategie.
