# H15 — i soldi passano prima, e noi arrivavamo dopo

**Registrata il 29/09 sera, prima di guardare qualunque numero sulle entrate anticipate.**

## Da dove nasce, per logica e non per speranza

Misurato oggi: chi compra **due ore** dopo la nascita del pool, con una taglia da cui si esce
davvero ($25–$50), incassa **circa zero prima dei costi** e perde l'1,8% di commissione.

Due cose sono vere insieme:
1. il gioco a +2h e' equo;
2. su questi pool qualcuno guadagna — i soldi dei perdenti finiscono da qualcuno.

Se valgono tutte e due, **chi guadagna era dentro prima delle due ore**. Non e' un'intuizione:
e' l'unica cosa che puo' reggere entrambe.

E' anche l'idea che Nicolo' aveva messo giu' ad agosto: i primi cento acquisti dal listino,
senza soglia d'importo, e la matrice wallet→finanziatore.

**Quella finestra non l'abbiamo mai misurata.** Quattordici ipotesi costruite tutte a valle del
punto dove i soldi passano di mano.

## L'ipotesi

> **H15: entrando a 3, 10 o 30 minuti invece che a 120, il fondale (nessuna selezione, taglia
> $25–$100, finestra da una settimana) e' positivo, e il vantaggio cresce quanto piu' presto
> si entra.**

## Come muore, deciso adesso

1. Serve il fondale **sopra +5%** a $100 — non sopra zero: sotto i cinque punti non copre
   nemmeno l'errore di misura di una finestra cosi' nervosa.
2. Serve su **tutte e due le chain**.
3. Serve **monotono**: 3 min meglio di 10, 10 meglio di 30, 30 meglio di 120. Un solo punto
   buono in mezzo a tre cattivi e' rumore, non un gradiente.
4. Serve che regga sulla **mediana**, non solo sulla media: se la media e' alta e la mediana
   e' a zero, e' un pugno di colpi fortunati.

## La trappola che mi aspetto, scritta prima di caderci

A tre minuti dalla nascita il prezzo d'ingresso `p0` e' **un singolo scambio**, e i primissimi
scambi di un pool nuovo possono essere a prezzi di avvio che non rappresentano niente. Un
guadagno costruito su un `p0` artificialmente basso e' **un artefatto**, non un vantaggio.

**Controllo obbligatorio prima di crederci:** se il guadagno c'e', va rifatto scartando il
primo scambio e usando il prezzo mediano dei primi cinque. Se sparisce, era l'artefatto.

## E una cosa che il numero non dira'

Anche se H15 sopravvive, **entrare a tre minuti non e' gratis**: bisogna accorgersi del pool,
decidere e comprare in tre minuti, su una catena, senza sbagliare. Quel costo qui non e'
misurato. Un vantaggio che esiste ma non e' raggiungibile resta un fatto interessante e non
un profitto.
