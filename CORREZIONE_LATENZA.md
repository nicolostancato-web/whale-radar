# Correzione: il crollo del 30 settembre non era la latenza

*1 ottobre 2026 · misurato a mano sui 48.467 pool di robinhood con almeno tre prezzi*

## Cosa avevo pubblicato

Il 30 settembre, in `LATENZA_LA_SCOPERTA.md`:

> «Con un solo scambio di ritardo il fondale passa da **+23,3% a −11,4%** e la migliore
> combinazione da +207% a +0,9%. Il prezzo che vedi non è quello che paghi.»

Su quel numero ho dichiarato morti tutti i vantaggi trovati fino a quel momento.

## Cosa c'era sotto

La funzione che calcola l'esito prendeva il prezzo d'acquisto così:

```python
p = 1.0 if r == 0 else cam[r - 1][1]
```

Con ritardo 0 **non divideva per un prezzo: divideva per uno**. Il «+23,3%» non era un
rendimento — erano dollari diviso 1,0. Un segnaposto che somigliava a un risultato.

Il confronto non era mai stato «prezzo osservato contro prezzo ottenibile»: era «numero
senza unità di misura contro un prezzo vero».

## La misura giusta

Calcolata a mano, senza passare da quella funzione, sugli stessi dati:

| come compro | media | mediana |
|---|---|---|
| al prezzo dello scambio su cui decido (**non ottenibile**) | **−5,0%** | −1,3% |
| al prezzo dello scambio **successivo** (ottenibile) | **−6,9%** | −1,4% |
| **quanto costa la latenza** | **−2,0 punti** | −0,1 punti |
| il segnaposto, per confronto (dividere per 1,0) | +28,6% | +2,0% |

**La latenza costa due punti sulla media e un decimo sulla mediana. Non trentacinque.**

## Cosa cambia, e cosa no

**Cambia la causa.** Non è la latenza che ha ucciso i vantaggi del 29-30 settembre: quei
vantaggi erano misurati contro un fondale che non era un fondale. Erano già morti prima,
per un motivo diverso — il «prima» a cui si confrontavano non esisteva.

**Non cambia il verdetto.** Entrambe le misure vere sono negative: comprando al prezzo
ottenibile si perde il 6,9% medio, comprando a quello che non si può avere il 5,0%. Il
gioco resta perdente a queste taglie, e la ragione non è la latenza — è il mercato.

**Cambia come si conta il ritardo.** Nel codice e nel registro delle prove:
`ritardo=1` è il prezzo dello scambio su cui si decide, **che non si può avere**;
`ritardo=2` è il primo prezzo che si può davvero pagare. Le prove da 1 a 27 girate a
`ritardo=1` misuravano quindi il prezzo non ottenibile. `ritardo=0` adesso **rifiuta**:
un argomento che non si può onorare non deve restituire un numero plausibile.

## La famiglia dell'errore

È la quarta volta in due giorni che lo stesso errore cambia vestito: **misurare il gesto
invece dell'esito.**

| quando | il gesto misurato | l'esito che contava |
|---|---|---|
| l'età di una corsia | il momento del lancio | l'ultimo lavoro riuscito |
| la soglia delle prove | le righe scritte nel registro | i 10.700 confronti dentro ogni giro |
| lo stato di una corsia | il verdetto del giro | i lavori veri dentro il giro |
| **il fondale** | **dollari diviso uno** | **dollari diviso un prezzo** |

E ogni volta il sintomo era lo stesso: **un numero plausibile dove doveva esserci un
rifiuto.** La difesa che resta scritta nel codice è sempre la stessa: quando non si può
onorare un argomento, si urla. Un segnaposto che somiglia a un risultato costa più di un
errore che si vede.
