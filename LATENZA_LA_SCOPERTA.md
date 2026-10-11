# La latenza uccide tutto — e uccide anche il numero di oggi

**30/09, notte. La correzione piu' importante del progetto: piu' grande della scoperta del
«quinto dei pool», perche' quella apriva una porta e questa la chiude.**

## Cosa abbiamo misurato per mesi

Il prezzo d'ingresso di ogni misura e' **il prezzo dello scambio a cui entriamo**. Sembra
ovvio: e' uno scambio realmente avvenuto, a quel prezzo qualcuno ha davvero comprato.

**Ma quel qualcuno non possiamo essere noi.** Per comprare si manda una transazione; quella
entra in coda e viene eseguita **dopo** gli scambi che la precedono. Il prezzo che si paga e'
quello dello scambio SUCCESSIVO, non quello che si sta guardando.

## Quanto costa un solo scambio di ritardo

Misurato sul cammino dei prezzi, 28.332 pool su robinhood:

| | mediana | q90 |
|---|---|---|
| prezzo del primo scambio dopo il mio, rispetto al mio | **1,025** | 1,91 |
| **sui pool a raffica** (quelli della combinazione) | **1,382** | 3,2 |

Sui pool veloci si paga il **38% in piu'**, in mediana. Nel 10% dei casi piu' del triplo.

## L'effetto su tutto quello che abbiamo trovato

Ricostruzione verificata fedele: a ritardo zero riproduce la misura ufficiale con **scarto
mediano zero**.

| ritardo | la combinazione trovata stanotte | il fondale «compra tutto» |
|---|---|---|
| **zero** (impossibile) | +207,2% | +23,3% |
| **un solo scambio** (il minimo reale) | **+0,9%** | **−11,4%** |
| due scambi | −1,3% | −8,1% |
| tre scambi | −4,7% | −9,3% |

**Tutto il vantaggio vive in un singolo scambio di latenza.**

## Cosa muore

1. **La combinazione di stanotte** (+193,8% su dati mai visti): muore. A un solo scambio di
   ritardo fa +0,9%, e la mediana e' −3,0%.
2. **Il +17,6% di oggi** — il primo numero positivo del progetto, quello del recap: **muore**.
   Assumeva di comprare al prezzo che si vede. A un solo scambio di ritardo il fondale e'
   **−11,4%**.
3. **Il contratto della prova in avanti** va riscritto: misurava l'esito comprando a un prezzo
   non ottenibile. Il giudice avrebbe dato un verdetto su un'illusione, con grande precisione.

## Cosa NON muore

- **Il metodo.** Tre pezzi di tempo, il controllo sul rumore, il conto delle combinazioni
  provate: tutto ha funzionato. Il motore ha trovato un pattern vero — un lancio con sei
  portafogli in sessanta secondi — e il pattern esiste. Non e' raggiungibile.
- **La scoperta del quinto dei pool.** Resta vera: la regola delle due ore escludeva la
  maggioranza dei pool. Cambia solo che anche quella maggioranza, comprata realisticamente,
  perde.
- **Le tre leve strutturali** (taglia, finestra d'uscita, momento): restano misurate. Vanno
  rimisurate col prezzo giusto.

## La lezione, e vale per ogni misura futura

> **Il prezzo che vedi non e' il prezzo che paghi. Il prezzo che paghi e' quello dello scambio
> dopo — e su un mercato che si muove in fretta, e' un mondo diverso.**

Astra l'aveva detto in forma generale stamattina: *«un vantaggio che esiste solo a latenza zero
non e' un vantaggio.»* Non l'avevo applicato al nostro stesso numero.

## Cosa faccio subito

1. **Aggiungere al dato l'esito con la latenza vera** (`_uscita_*_ritardo`): da ora ogni misura
   nasce con il prezzo ottenibile, non con quello osservato. Il vecchio campo resta, per poter
   confrontare — ma non e' piu' quello su cui si decide.
2. **Riscrivere il contratto della prova in avanti** su quel campo.
3. **Rifare la ricerca delle combinazioni** con la latenza dentro: se esiste un pattern che
   sopravvive a uno, due, tre scambi di ritardo, quello e' un vantaggio vero. Se non esiste,
   lo sapremo con la stessa chiarezza.
