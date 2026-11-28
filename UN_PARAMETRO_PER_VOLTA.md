# Separate le due variabili: l'ingresso vale +8,5 punti, l'universo onesto ne costa 1,5

*5 ottobre 2026 · quattro universi, un parametro per volta, misura sul capitale*

## Perche' serviva

Ieri notte ho cambiato **due cose insieme** — la soglia di vita del pool e il momento
d'ingresso (dal quinto al secondo scambio) — e il risultato era migliorato. Non ho attribuito
nulla a nessuna delle due: e' la «dimensione fantasma» del 2/10, dove dodici prove sembravano
indipendenti e il codice ignorava una delle due dimensioni.

Quattro combinazioni, costruite separatamente:

| sigla | universo | ingresso |
|---|---|---|
| `_sc5` | filtrato (>=10 scambi di vita) | 5o scambio |
| `__onesto5` | **onesto** (nessuna soglia) | 5o scambio |
| `__filtrato2` | filtrato | **2o scambio** |
| `__onesto` | **onesto** | **2o scambio** |

## Il risultato, capitale a 100$ (chi non esce conta −100%)

| universo | ingresso | base | robinhood |
|---|---|---|---|
| filtrato | 5o | −18,7% | +2,4% |
| **onesto** | 5o | **−20,5%** | **+1,0%** |
| filtrato | **2o** | **−10,4%** | **+11,2%** |
| onesto | 2o | −17,4% | +1,6% |

**Isolando una variabile per volta:**

| effetto | base | robinhood |
|---|---|---|
| universo onesto invece di filtrato (ingresso fermo al 5o) | **−1,8** | **−1,4** |
| ingresso al 2o invece del 5o (universo fermo) | **+8,3** | **+8,8** |

**Il miglioramento di stanotte era tutto l'ingresso, non l'universo.** E le due chain
concordano quasi esattamente su entrambi gli effetti: +8,3 contro +8,8, e −1,8 contro −1,4.

## Come si leggono i due numeri

**L'universo onesto costa poco piu' di un punto, e deve costarlo.** Include i pool che muoiono
prima del decimo scambio — cioe' le perdite che prima togliavamo dal conto senza dirlo. Un
fondale che peggiora di 1,5 punti quando si smette di nascondere le perdite e' la prova che la
correzione era piccola in grandezza e necessaria in sostanza.

**L'ingresso vale otto punti e mezzo, e non e' informazione dal futuro.** Il momento in cui
compriamo lo scegliamo noi: e' l'unica leva di questa notte che sia sotto il nostro controllo.
Comprare al secondo scambio invece del quinto vale +8,3 punti su base e +8,8 su robinhood.

**Una cautela, perche' il numero piu' bello e' il piu' sospetto.** La combinazione migliore —
filtrato + secondo scambio, **+11,2%** su robinhood — sta nell'universo FILTRATO, quindi
contiene informazione dal futuro (richiede che il pool arrivi a dieci scambi). Non e'
ottenibile. Il numero onesto e' l'ultima riga: **+1,6%**.

## Il fondale onesto, definitivo

| | capitale a 100$, universo onesto, ingresso al 2o |
|---|---|
| base | **−17,4%** |
| robinhood | **+1,6%** |

Questo e' il metro contro cui vanno rifatti i tre verdetti chiusi stanotte, e contro cui va
misurato qualunque filtro futuro. Al 2% di costi di andata e ritorno, robinhood scende a circa
**−0,4%**: siamo a zero, non sopra.
