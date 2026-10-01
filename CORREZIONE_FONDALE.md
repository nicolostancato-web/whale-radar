# Correzione — il fondale non misurava chi tiene, misurava chi liquida subito

**29/09, sera. Corregge la lettura di tutti i numeri pubblicati oggi.**

## Cosa ho detto e cosa era vero

Ho scritto piu' volte, oggi, che allungando la finestra «il fondale migliora di quattordici
punti» e l'ho raccontato come **guadagno di chi tiene piu' a lungo**.

E' sbagliato. La simulazione di vendita comincia a vendere **l'istante dopo l'acquisto** e
prende i prezzi come arrivano finche' i $500 sono piazzati. Quello che non riesce a vendere
entro la finestra **vale zero**.

Quindi la finestra non e' «quanto tengo»: e' **quanto tempo ho per uscire**.

| finestra | quanto dei $500 si riesce a vendere | robinhood | base |
|---|---|---|---|
| 6 ore | | 65,3% | 46,7% |
| 24 ore | | 76,9% | 59,4% |
| una settimana | | 85,1% | 70,4% |
| un mese | | 88,9% | 75,8% |

A sei ore un terzo della posizione restava invenduta e contava zero. **Da sola, quella e' quasi
tutta la voragine del −53%.**

## Perche' conta piu' della correzione in se'

La frase «questo mercato crolla del 53% in sei ore» e la frase «in sei ore non riesci a uscire»
descrivono lo stesso numero e portano a due lavori completamente diversi:

- la prima dice **non entrare**;
- la seconda dice **entra con una taglia da cui puoi uscire**.

Per settimane abbiamo cercato quale pool comprare. La misura diceva, senza che la leggessi
bene, che il problema non era la scelta: era **la taglia rispetto alla porta d'uscita**.

## Come l'ho scoperto, che e' la parte utile

Avevo previsto che H14 (vendere a 2x) **peggiorasse** passando dal prezzo all'incasso. Invece
e' migliorata: da +5,6 a +24,4 punti. Un risultato che migliora **contro la mia previsione** e'
il segnale piu' affidabile che ho di un mio errore, e questa volta l'ho seguito invece di
festeggiare.

> **Quando un numero va meglio di come lo avevi previsto, cercalo l'errore prima di cercare la
> spiegazione. La spiegazione la trovi sempre; l'errore solo se lo cerchi.**

## Verdetto su H14, con la regola scritta prima

| | robinhood | base |
|---|---|---|
| vendere dal primo scambio a 2x, $500 veri, fuori campione | **+17,8%** (+24,4 punti) | −24,8% (−0,1) |

**Non passa.** La regola registrata chiedeva tutte e due le chain; base non si muove di un
decimo di punto. Una chain sola e' rumore, e 371 pool fuori campione sono pochi.

Resta come la cosa piu' promettente vista finora, con la soglia gia' fissata per crederci:
**2.000 pool fuori campione, positivo su tutte e due.**
