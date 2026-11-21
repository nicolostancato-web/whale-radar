# Esiste, ma è sottile — 6 ottobre 2026, notte

## Il primo risultato della giornata che regge su uno strumento verificato

| | |
|---|---|
| operatori che vendono, con ≥50 posizioni pulite | 1.285 |
| **guadagnano in entrambe le metà della propria storia** | **181** |
| quanti ne spiegherebbe il caso (20 giri) | min 7, mediana 17, **massimo 24** |
| **eccesso oltre il caso** | **164 operatori** |
| | **7,5 volte il massimo del caso** |

**Il vantaggio esiste e non è sorteggio.**

## Ma è sottile, e il numero va detto subito

I 181 che reggono hanno un **ritorno mediano di 1,049x**. Il migliore fa **1,517x**. Solo 20
superano 1,2x, e **uno solo** supera 1,5x.

Non è «da 50 euro a 500». È un margine del 5% nella mediana, del 52% nel caso migliore — e lo
slittamento, quando a comprare siamo noi, non è ancora incluso.

## Perché questa volta ci credo: il criterio l'ho fissato prima

Un metro vuoto vale solo se i portafogli **finti partono dalla stessa mediana dei veri**
(scarto < 0,03). Se il finto tipico perde più del vero tipico, il metro dichiara bravo chiunque.

**Ho costruito sette metri. I primi sei li ho buttati io**, perché nessuno passava quel criterio:

| metro | finti | contro veri | scarto |
|---|---|---|---|
| 1. rimescolare tutte le posizioni | 0,581x | 0,848x | −27 punti |
| 2. appaiato per periodo e taglia | 0,581x | 0,848x | −27 |
| 3. appaiato anche sul tipo di operatore | 0,688x | 0,848x | −16 |
| 4. pescare il multiplo, tenere la puntata | 0,689x | 0,848x | −16 |
| 5. peso uguale per portafoglio | 0,595x | 0,848x | −25 |
| **7. solo fra chi vende** | **0,931x** | **0,943x** | **−1,2** ✓ |

## Il difetto comune dei sei, e come l'ho trovato

Nel mazzo c'erano i portafogli **che non vendono mai**: 451 su 1.841, che comprano 50-130 monete e
non ne vendono nessuna. Mescolarli con chi commercia abbassava il metro di venti punti.

**L'ho verificato sulla chain invece di assumerlo:** 8 di quei portafogli, 24 curve controllate,
**zero vendite che i miei dati si fossero persi**. Non è un buco nostro, è comportamento vero.

E un dettaglio che cambia la lettura: su una curva si può **sempre** rivendere, anche in perdita.
Quindi quei 451 non *non potevano* uscire — **hanno scelto di non farlo**. Sono un'altra specie,
non un termine di paragone.

## Cosa questo NON dimostra

**Che sia copiabile.** Dimostra che non è sorteggio. Fra «esiste qualcuno più bravo» e «possiamo
guadagnare copiandolo» c'è ancora tutto:

- il test del copiatore con **regola congelata**, applicata in avanti, comprando *anche* le monete
  che vanno a zero (lo chiedono sia Astra sia Grok);
- lo **slittamento**: a quelle taglie noi muoveremmo il prezzo quanto loro, ma dopo di loro;
- **tre fette su dieci della finestra storica sono ancora al 63%, 20% e 28%**. Il numero può
  cambiare quando saranno complete.

## Il bilancio di una giornata

Sette oggetti promettenti. **Sei smontati**, l'ultimo regge:

1. «+21% a chi entra primo» → sopravvivenza
2. «157x» → vendeva cento volte i gettoni che aveva comprato
3. la firma d'ingresso dei sette → artefatti
4. «le graduate rendono 0,29x» → vedevo l'1,6% di chi scambia
5. «129 contro 0» → metro storto di 16-27 punti
6. «chi rende non compra cadaveri» → era osservabilità
7. **«181 contro 24, su un metro validato»** → **regge**

Il meccanismo è in `agents/metro_dei_bravi.py`, collegato alla corsia `curva_lanci`: il criterio di
validità è dentro il codice, e se un giorno il metro non lo passa, **l'agente si rifiuta di
scrivere il verdetto**.
