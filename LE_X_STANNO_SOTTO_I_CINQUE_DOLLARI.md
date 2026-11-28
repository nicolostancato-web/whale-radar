# Le X stanno sotto i cinque dollari — 7 ottobre 2026

## L'obiezione di Nicolò, e perché aveva ragione

> *«Mi parli di percentuali assurde, 5%. Queste monete hanno capitali vergognosamente bassi.
> Basta che da 1 milione va a 2 milioni ed è il 100%. Come fa il 5%?»*

Aveva ragione, e il mio numero era **nascosto da un mio filtro**. Avevo fissato la banda «la nostra
taglia» a 0,01-0,2 di valuta nativa senza sapere quanto valessero in euro: sono **26-515 dollari**.
E in quella banda il multiplo mediano è davvero 1,05x. Ma le X non stanno lì.

## La tabella, per quanto si mette

| quanto mette | giri | mai uscito | multiplo mediano | ≥10x | ritorno sul capitale |
|---|---|---|---|---|---|
| **sotto 1 $** | 316 | 12% | **21,8x** | **87%** | 22,2x |
| **1 – 5 $** | 500 | 10% | **25,5x** | **74%** | 22,5x |
| 5 – 26 $ | 907 | 18% | 1,06x | 8% | 21,7x |
| 26 – 100 $ | 951 | 22% | 1,07x | 1% | 1,36x |
| 100 – 515 $ | 1.688 | 17% | 1,04x | 0% | 1,02x |
| oltre 515 $ | 1.314 | 13% | **0,96x** | 0% | 0,90x |

**Il multiplo è una funzione brutale della taglia.** Sotto i 5 dollari si fa 22-25x in mediana;
sopra i 515 si perde. Ha un senso meccanico: su un pool minuscolo una puntata da 500 dollari
**si compra il proprio rialzo**, una da 2 dollari no.

## La banda sotto 5 dollari, in dettaglio

| | |
|---|---|
| giri | **816** su 748 portafogli distinti |
| messo in tutto | **$1.309,59** |
| incassato | **$29.368,46** |
| ritorno | **22,43x** |
| senza la posizione migliore | 17,44x |
| senza le prime 10 | 16,60x |
| **senza il 10% migliore (81 giri)** | **14,17x** |
| guadagno mediano per giro | **$18,40** |
| il colpo più grosso | messo **$1,92**, incassato **$6.565** (3.428x) |

**Regge alla rimozione degli estremi**: anche togliendo il 10% migliore resta 14x. Non è
l'artefatto che ieri ha ucciso il «157x».

## Un artefatto che ho trovato e rimosso prima di pubblicare

Nella prima versione il massimo della banda più bassa era **861.619x**, e il ritorno sul capitale
**251x**. Causa: **2.471 posizioni in cui non vedo l'acquisto**, e il mio codice assegnava loro come
costo solo il gas (2 centesimi). Dividere un incasso per 2 centesimi dà numeri astronomici che non
sono guadagni: sono **un costo che non ho visto**.

Escluse, il massimo scende a 81x e il ritorno a 22x. Decima volta in due giorni che un dato
mancante viene trattato come un numero — e la decima volta che il controllo lo prende.

## Cosa questo NON dice ancora

1. **Non dice che possiamo farlo noi.** Il guadagno mediano è **$18,40 per giro**: per fare soldi
   veri servono centinaia di giri, e la domanda «riusciamo a entrare al prezzo che hanno avuto
   loro?» è esattamente quella su cui la strada della curva è caduta.
2. **748 portafogli per 816 giri**: quasi tutti ne hanno fatto **uno**. Quindi non c'è ancora
   prova di ripetibilità — il più attivo ne ha fatti 13.
3. **La copertura è parziale** e il metro del caso non è ancora applicabile.
4. E il sospetto da escludere: questi potrebbero essere **gli indirizzi esentati dalla tassa** o
   gli insider del lancio. Vanno identificati e tolti, come si è fatto con i lanciatori.

## La correzione a me stesso

Avevo detto a Nicolò «+5%» presentandolo come il risultato del mercato pubblico. Era vero per la
banda che avevo scelto io, e **la scelta era arbitraria e mal informata**: non avevo convertito la
valuta in dollari prima di decidere cosa fosse «la nostra taglia».

Lezione: **prima di fissare una soglia, convertirla nell'unità in cui si pensa.** Una banda in
unità di valuta nativa non dice niente a nessuno, nemmeno a chi la scrive.
