# Chi entra all'inizio fa tante X? — 6 ottobre 2026, 16:30

## La domanda, e perché si può rispondere senza prezzi

Nicolò: *«dobbiamo capire se c'è gente che entra all'inizio all'inizio e fa tante X… con quanti
soldi investono all'inizio e con quanti se ne portano a casa.»*

Il giro è: **paga sulla curva → la moneta gradua → vende nel pool**. Curva e pool si pagano nello
stesso asset, quindi il multiplo è un **rapporto fra quantità della stessa cosa**: zero prezzi,
zero conversioni, zero modo di sbagliare le unità. Dove gli asset sono diversi, la posizione si
**scarta e si conta** — non si converte.

## Il primo numero, con l'ordine di arrivo

Finestra piccola (436 curve), **solo** i portafogli della nostra lista, 1.008 giri completi:

| posizione in fila | casi | mediana | 90° percentile | ≥2x | ≥10x | massimo |
|---|---|---|---|---|---|---|
| **1°** | 72 | **0,941x** | 1,64x | 9,7% | **2,8%** | **84,5x** |
| 2° | 59 | 0,954x | 1,99x | 10,2% | 0% | 8,3x |
| 3° | 48 | 0,924x | 1,33x | 6,2% | 0% | 2,5x |
| 5° | 40 | 0,926x | 1,24x | 7,5% | 0% | 9,7x |
| 10° | 28 | 0,774x | 0,98x | 3,6% | 0% | 2,0x |
| 20° | 15 | 0,412x | 0,99x | 6,7% | 0% | 2,5x |

**L'ordine conta, e si vede.** La mediana scende dal 94% al 41% man mano che si entra più tardi, e
la coda destra è dei primi: l'unico 84x e l'unico 2,8% sopra 10x stanno in prima posizione.

**Ma la mediana è sotto 1 ovunque.** Il compratore tipico, anche il primo, perde circa il 6%. Se
c'è guadagno, è nella coda — non nel caso tipico.

## Il numero che deciderebbe, e perché non ce l'abbiamo ancora

Con una coda grassa la mediana non basta: serve il **ritorno sul capitale** (se scommetto la
stessa cifra su ognuno, quanto torna in tutto). L'ho calcolato, ed è **instabile**: 0,03x per la
prima posizione, 1,33x per la seconda, 0,75x per la terza.

Non è un risultato contraddittorio: è un **campione troppo piccolo e troppo concentrato**.
Misurato:

| posizione | la scommessa più grossa pesa |
|---|---|
| 1° | 22% di tutto il capitale |
| 2° | **65%** |
| 3° | 41% |
| 5° | 53% |

Con una sola posizione che vale fino a due terzi del totale, quel numero lo decide un singolo
scambio, non una tendenza. **Quindi non lo pubblico come stima.** Serve più copertura.

## Tre difetti trovati in questo giro, tutti sulle unità

1. **I campi della vendita erano invertiti** rispetto all'acquisto (gettoni dove c'era il denaro).
   Scoperto da un multiplo da 306 milioni. È la stessa assunzione di simmetria del 5 ottobre:
   seconda volta in due giorni.
2. **Le somme non dicevano se l'importo era grezzo o convertito.** Due numeri identici all'occhio
   e diversi di 10¹⁸: mescolandoli sono usciti multipli da 5 miliardi di miliardi. Ora l'unità
   **viaggia dentro ogni voce**, e chi legge si rifiuta di sommarne due diverse. Avevo visto
   questa lacuna la mattina e non l'avevo chiusa.
3. **Una riga di stampa che spariva.** Un condizionale messo sulla stringa intera invece che su un
   campo: senza quel campo la riga non si mostrava incompleta, **non si mostrava affatto**. Una
   riga che scompare è un dato che non esiste.

Tutti e tre venivano dallo stesso posto: **un numero senza la sua unità accanto.**

## Dove si guarda, e cosa manca

`agents/x_di_chi_entra_prima.py`, collegato alla corsia `curva_lanci` nello stesso lavoro che
produce l'elenco dei lanci e la riconciliazione.

Manca: più copertura (tre fette su dieci sono ripartite da zero per riparare le unità), e **il
costo del gas**, che su posizioni da pochi centesimi può decidere il segno. È la prima cosa da
aggiungere se un multiplo risulta appena sopra 1.
