# Il limite della taglia — questo mercato e' un gioco equo, e noi paghiamo la commissione

**29/09, sera. La misura che chiudeva o apriva il progetto.**

## La domanda

L'ordine delle taglie regge su otto epoche su otto: piu' piccolo e' sempre meglio. Quindi:
**dove si ferma?** Se anche a venticinque dollari il fondale resta negativo, nessuna taglia
salva il mercato.

## La risposta

robinhood, finestra da un mese, 723 pool:

| taglia | media tagliata | mediana | venduto |
|---|---|---|---|
| $2000 | −17,4% | −4,6% | 79% |
| $500 | −9,0% | −3,0% | 88% |
| $100 | −3,1% | −2,3% | 96% |
| $50 | −2,2% | −2,1% | 97% |
| **$25** | **−2,2%** | **−2,0%** | **98%** |

**Converge, e non a zero: a circa −2%.**

E il costo di giro che sottraiamo e' **1,8%** (`COSTO_GIRO` in insieme.py).

> **Comprare un memecoin a caso due ore dopo la nascita, con una taglia da cui si esce davvero,
> rende circa ZERO prima dei costi. E la commissione lo porta sotto.**

## Cosa significa, detto senza ammorbidire

Il **−53%** da cui siamo partiti stamattina non era il mercato che deruba chi entra. Era la
nostra taglia che non passava dalla porta d'uscita: a $500 e sei ore si vendeva il 58% della
posizione, e il resto contava zero.

Tolto quell'artefatto, sotto c'e' **un gioco equo**. Che e' esattamente quello che ci si aspetta
da un mercato dove nessuno ha un vantaggio: il prezzo medio a cui si compra e quello a cui si
vende coincidono, e la differenza la prende chi fa da tramite.

**Un gioco equo meno le commissioni e' un gioco perso.** Senza un vantaggio nella scelta, non
c'e' nessuna taglia, nessuna finestra e nessuna regola d'uscita che faccia soldi.

## E il vantaggio nella scelta?

Quattordici ipotesi. Sul campione grande, il decimo migliore scelto dal modello fa **peggio del
caso** su tutte e due le chain (−32,9% contro −14,5%; −23,0% contro −14,1%).

## Dove resta qualcosa da guardare

Se chi compra a +2h esce in pari, i soldi che passano di mano li prende **chi era dentro
prima**. Non e' una deduzione elegante: e' l'unica cosa che puo' essere vera se il gioco a +2h
e' equo e qualcuno guadagna.

Ed e' esattamente l'idea che Nicolo' aveva messo giu' ad agosto — i primi cento acquisti dal
listino, senza soglia, e la matrice wallet→finanziatore per riconoscere chi cambia portafoglio
ma non identita'.

**Non abbiamo mai misurato quella finestra.** Abbiamo sempre guardato da +2h in poi, cioe' da
dopo che i soldi erano gia' passati.

## La lezione

> **Quando un mercato sembra derubare tutti, prima di spiegarlo controlla se stai misurando
> il mercato o il tuo stesso ordine.**

Per settimane il numero che chiamavamo «il fondale di questo mercato» era, in buona parte, il
costo di provare a uscire con troppi soldi in troppo poco tempo.
