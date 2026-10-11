# I campi della vendita erano invertiti — 6 ottobre 2026, 15:30

## Il difetto

L'evento di acquisto e quello di vendita sulla curva hanno la **stessa firma**, e io ho assunto
che avessero anche lo **stesso ordine dei campi**. Non è così:

| evento | campo 0 | campo 1 |
|---|---|---|
| `CurveBuy` | valuta che **entra** | gettoni che **escono** |
| `CurveSell` | gettoni che **entrano** | valuta che **esce** |

Quindi su ogni vendita leggevo i gettoni come denaro e il denaro come gettoni.

**È la stessa assunzione di simmetria** che il 5 ottobre ci aveva fatto invertire acquisti e
vendite sul 67-78% dei pool. Due eventi con la stessa firma non hanno per forza lo stesso
significato nello stesso posto. Seconda volta in due giorni.

## Come è saltato fuori

Non da un controllo: da un numero assurdo. Misurando il multiplo per posizione in fila è uscito
**306.256.452x** per il secondo arrivato. Un numero così non è un risultato, è un sintomo.

## La prova, che non è un'interpretazione

In una vendita vera: campo 0 = `24.326.879.850.071.016.010.754.537`, campo 1 =
`43.198.716.754.653.951`. Nella **stessa transazione** ci sono due trasferimenti:

- esattamente `24.326.879.850.071.016.010.754.537` **memecoin** dal venditore alla curva;
- esattamente `43.198.716.754.653.951` di **valuta** dalla curva al venditore.

Due trasferimenti che combaciano alla cifra. Non serve interpretare.

## Cosa invalida di quello che avevo già pubblicato

Stamattina ho pubblicato *«I gettoni tornano»*. Vado per gradi, senza ammorbidire:

**Regge:** i 43 casi impossibili diventati zero. Quel risultato dipende dagli **acquisti** sulla
curva, che erano letti correttamente.

**Da rifare:** la mediana di 0,98 e il 53% che quadrava. Il conto usava
`gettoni comprati − gettoni venduti` sulla curva, e i «gettoni venduti» erano in realtà un
importo in valuta, cioè un numero piccolissimo: in pratica **le vendite sulla curva venivano
ignorate**. Per chi aveva rivenduto lì, sovrastimavo i gettoni portati al pool.

**La direzione dell'errore è nota:** correggendolo il numero netto scende, quindi il rapporto
sale. La mediana vera è **≥ 0,98**, non meno. Ma il valore esatto va rimisurato, e lo rimisuro.

## Il primo numero col lato vendita giusto

Su una finestra piccola (308 curve, 1,7 ore di chain), **solo** per i giri che cominciano e
finiscono sulla curva:

| posizione in fila | casi | multiplo mediano | sopra 2x | sopra 10x |
|---|---|---|---|---|
| 1° | 127 | 0,94x | 6% | 2% |
| 2° | 134 | 0,95x | 5% | 0% |
| 3° | 107 | 0,96x | 1% | 0% |
| 5° | 76 | 0,98x | 3% | 0% |
| 10° | 53 | 0,92x | 0% | 0% |

**Attenzione a cosa NON dice questa tabella.** Misura solo chi entra ed esce **sulla curva**,
cioè in gran parte monete che non arrivano mai al mercato pubblico. Chi fa i colpi grossi
presumibilmente esce **nel pool dopo la graduazione**, e quel pezzo qui non c'è.

Quindi: non è ancora un verdetto, è il primo numero non sbagliato.
