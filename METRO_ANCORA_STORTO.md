# Il metro è ancora storto — 6 ottobre 2026, notte

## Il risultato che NON pubblico come prova

Fra gli operatori attivi (≥50 operazioni pulite nella nostra taglia), **129 su 1.841 reggono la
prova a metà**: guadagnano in entrambe le metà cronologiche della propria storia. Il metro vuoto
ne dà **zero**, cinque volte su cinque.

129 contro 0 sembra schiacciante. **Non lo pubblico come prova, perché il metro è tarato male e
posso dimostrarlo.**

## Come l'ho scoperto

Invece di festeggiare lo zero, ho controllato se il metro funziona. Basta guardare la mediana:

| | mediana | 90° | 99° | massimo | sopra 1x |
|---|---|---|---|---|---|
| portafogli **veri** | 0,848x | 1,012x | 1,197x | 1,470x | 14,1% |
| portafogli **finti** | 0,581x | 0,709x | 0,809x | 1,054x | 0,1% |

Il finto tipico perde il 42%, il vero il 15%. **Un metro che parte 27 punti più in basso dichiara
bravo chiunque.**

## Tre tentativi, tre errori diversi

1. **Rimescolare fra tutte le posizioni.** Prendeva anche i centomila portafogli che fanno una
   sola operazione, che vanno molto peggio: confrontavo un operatore attivo con un passante.
2. **Appaiare per periodo e taglia.** Meglio, ma non basta: mediana dei finti 0,581x.
3. **Appaiare anche sul tipo di operatore** (pescare solo fra posizioni di chi ha ≥50 operazioni).
   Migliora a 0,688x, ma resta 16 punti sotto i veri.

## Perché il terzo è ancora storto, e credo di sapere il motivo

Pescando dal mazzo comune ottengo una media **pesata per capitale**, dominata dai portafogli che
mettono le cifre più grosse dentro la banda — e quelli vanno peggio. Quindi confronto il
portafoglio tipico con una media che non è la sua.

Il quarto tentativo deve appaiare ogni portafoglio al **proprio profilo di taglia**, non al mazzo:
i finti devono avere la stessa distribuzione di puntate, non solo lo stesso scaglione.

## Perché lo scrivo invece di tacerlo

Perché è la quarta volta oggi che un risultato entusiasmante era un difetto di misura: il «+21% a
chi entra primo» (sopravvivenza), il «157x» (gettoni non bilanciati), la firma dei sette
(artefatti), e ora «129 contro 0» (metro storto).

Tre volte l'ho scoperto dopo aver pubblicato. **Questa l'ho scoperta prima**, e la differenza
l'ha fatta una sola abitudine: quando un numero è troppo bello, controllare lo strumento invece
del risultato.

**Il candidato `0x6a96de27…` resta valido per quello che era già verificato** — i gettoni tornano,
le transazioni esistono, guadagna in entrambe le metà. Quello che NON è ancora dimostrato è che
sia **distinguibile dagli altri 1.840**: per dirlo serve un metro che non parta storto.
