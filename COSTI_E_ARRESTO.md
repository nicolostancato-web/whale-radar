# Il +1,0% di ieri era il punto di arresto. Scelto in anticipo, fa −4,1%.

*4 ottobre 2026 · robinhood a tre momenti d'ingresso, base a uno, costi contati*

## Le due cose che mancavano, aggiunte

Ieri (`A_ZERO_NON_SOTTO.md`) ho riferito **+1,0%** e ho scritto io stesso, nello stesso
documento, che il punto dove fermare i filtri l'avevo scelto guardando la curva. Oggi l'ho
fatto come si deve, e il numero e' caduto. Si misura anche questo: **meno di un giorno fra
nominare il rischio e ucciderlo.**

1. **Il punto di arresto si scegli sul pezzo di SCELTA.** Quante soglie impilare lo decide il
   pezzo intermedio; il pezzo mai visto si legge una volta sola, con quel k, e basta.
2. **I costi si contano**, a livelli dichiarati prima di guardare: andata+ritorno all'1%, 2%
   e 5%. Il costo non si applica a chi e' morto — se la pool va a zero hai perso tutto
   comunque, non −100% meno il 2%.

## Il conto

| | k scelto | 0% | 2% | 5% | copre | muoiono |
|---|---|---|---|---|---|---|
| robinhood ingresso 5 | 5 | −2,2% | **−4,1%** | −7,0% | 28,6% | 3,5% ← 8,6% |
| robinhood ingresso 10 | 1 | −6,8% | −8,7% | −11,6% | 62,5% | 3,3% ← 5,4% |
| **robinhood ingresso 25** | 5 | +3,4% | **+1,4%** | −1,5% | 35,2% | 1,8% ← 4,1% |
| base ingresso 5 | 3 | −16,0% | −17,8% | −20,5% | 34,1% | 10,2% ← 29,9% |

**Tre casi su quattro sono negativi dopo i costi.** Sul dataset dove ieri avevo letto +1,0%,
il k scelto in anticipo da **−4,1%** — e persino il k *migliore in retrospettiva* su quel
pezzo sarebbe stato −0,9%, cioe' sotto zero comunque. Il +1,0% non era un risultato: era il
punto piu' bello di una curva.

## Cosa resta in piedi, ed e' molto

Lo **scarto** contro il mercato e' positivo **4 volte su 4**, e i costi non lo toccano:

| | scarto a 0% | a 2% | a 5% |
|---|---|---|---|
| robinhood ingr. 5 | +9,5 | +9,4 | +9,2 |
| robinhood ingr. 10 | +1,2 | +1,2 | +1,1 |
| robinhood ingr. 25 | +6,4 | +6,3 | +6,3 |
| base ingr. 5 | +25,5 | +25,1 | +24,5 |

I costi non mangiano il vantaggio perche' **il filtro non cambia quanto paghi: cambia in quali
pool stai.** E il tasso di morte scende 4 volte su 4, fino a dimezzarsi o meglio.

Quindi: **il filtro e' reale e regge, ma non e' un profitto.** Toglie perdita a un gioco che
resta perdente.

## Il filo nuovo, che non cercavo

Guardando la colonna del mercato: **piu' tardi si entra, meno e' letale.** Ingresso 5 →
−11,7%; ingresso 10 → −8,0%; ingresso 25 → −3,0%. Monotono. E l'unico caso che passa lo zero
dopo i costi e' il piu' tardivo.

E' l'opposto di come abbiamo ragionato per settimane (prendere la moneta il prima possibile,
«nei primi secondi»). Vale una misura dedicata: **il rendimento al netto dei costi come
funzione del momento d'ingresso**, su tutti i dataset che abbiamo, non su tre.

## SMENTITO lo stesso giorno: il momento d'ingresso non conta

La regolarita' qui sopra («piu' tardi si entra, meno e' letale», −11,7% → −8,0% → −3,0%) l'avevo
letta sul **pezzo di giudizio**, cioe' l'ultimo 28% di ciascun dataset: finestra temporale
diversa per ogni momento d'ingresso, e campione piccolo. Sulla popolazione **intera** la curva
e' piatta:

| ingresso | pool | medio | netto al 2% | mediano | muoiono |
|---|---|---|---|---|---|
| 5 | 21.791 | −5,5% | −7,4% | −1,8% | 4,6% |
| 10 | 8.351 | −5,4% | −7,3% | −1,7% | 4,1% |
| 25 | 7.245 | −4,7% | −6,7% | −1,7% | 3,6% |
| 60 | 5.833 | −5,0% | −6,9% | −1,7% | 3,3% |

Era la spiegazione **(b)** delle tre che avevo scritto in `curva_ingresso.py` PRIMA di girare:
arrivare allo scambio 60 e' esso stesso un filtro di sopravvivenza — i pool crollano da 21.791
a 5.833 — e il rendimento non migliora di conseguenza. La mediana non si muove di un decimo.

**Il momento d'ingresso non e' una leva.** Il filo si chiude qui, nello stesso giorno in cui si
e' aperto, e la smentita sta accanto all'affermazione invece che al posto suo.

## Una lezione di mestiere, scritta dove serve

`arresto_dichiarato.py` moriva con «index −1 is out of bounds»: venti righe di traccia che non
nominano la causa. La causa era che lo storico dei compratori non era sul disco, quindi nessuna
riga aveva l'attributo e il mazzo era vuoto. Ora il programma si ferma dicendo **quale file
manca e cosa comporta**. Un programma che muore senza dire perche' costa piu' di uno che non
gira.
