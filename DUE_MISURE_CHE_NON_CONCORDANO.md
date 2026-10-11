# Due misure della stessa cosa non concordano, e lo dico prima di scegliere quale mi piace

*5 ottobre 2026 · il test del ritardo, e cosa ha fatto emergere*

## Il test del ritardo: la risposta e' zero

Ricostruendo le operazioni dei portafogli bravi **al prezzo della pool** — comprando al primo
scambio avvenuto dopo il ritardo, vendendo al prezzo di quando hanno venduto loro, e contando
−100% dove non c'era nessuno scambio:

| ritardo | base (750 op.) | robinhood (1.072 op.) | in utile (robinhood) |
|---|---|---|---|
| 0s | −0,1% | **−0,1%** | 47,9% |
| 60s | −0,0% | −0,0% | 48,7% |
| 300s | −0,1% | −0,0% | 48,7% |
| 3.600s | −0,4% | −0,7% | 44,3% |

**La mediana e' zero a ogni ritardo, e il colpo va in utile nel 48% dei casi: una monetina.**
Nota che il ritardo in se' quasi non conta — il che e' informativo: non stiamo perdendo il
vantaggio *arrivando tardi*, perche' a quel prezzo non c'era vantaggio nemmeno a ritardo zero.

## Ma il conto in dollari dice un'altra cosa

Sulle posizioni chiuse con **costo sopra 100$** (dove l'arrotondamento non puo' spiegare
niente): 22 portafogli su robinhood, **468$ di utile mediano per operazione** su 207$ spesi,
14,7 operazioni al mese.

## Quello che ho dimostrato: il multiplo era gonfiato

| costo registrato | multiplo mediano, base | robinhood |
|---|---|---|
| sotto 1$ | **55,75X** | **65,53X** |
| 1–10$ | 2,12X | 6,28X |
| 10–100$ | 1,25X | 2,82X |
| sopra 100$ | **1,05X** | **1,41X** |

Il multiplo **scala inversamente alla dimensione**, in modo troppo pulito per essere un fatto
di mercato. E' la firma di un **denominatore sottostimato**: piu' piccolo il costo registrato,
piu' grande il multiplo apparente. Dove il costo e' credibile il multiplo e' 1,05X e 1,41X,
vicino all'1,00X misurato sui prezzi.

**Quindi il «3-6X» di stamattina era un artefatto.** Questo e' dimostrato.

## Quello che NON ho dimostrato, e per questo il numero di stamattina non va usato

Le due misure guardano insiemi diversi:

- **in dollari**: solo le posizioni chiuse sopra 100$ di portafogli **gia' selezionati** per
  avere multipli alti;
- **al prezzo**: **tutte** le loro coppie compra-vendi, selezionate o no.

Possono essere entrambe vere se il guadagno si concentra in una minoranza di operazioni. Ma
**non l'ho verificato**, e finche' non lo verifico il «4.200$ al mese per portafoglio» che ho
riferito stamattina **non va usato**. Era costruito su `incassato − speso` con `speso`
sottostimato.

## Il test che scioglie il nodo, dichiarato prima

Prendere **le stesse** operazioni — stesso portafoglio, stesso pool, stesso istante — e
misurarle nei due modi, una per una. Se il rapporto fra le due misure e' vicino a uno, il conto
in dollari e' sano e la mediana zero riguarda operazioni diverse. Se il rapporto e'
sistematicamente maggiore di uno, il conto in dollari e' gonfiato anche sopra i 100$ e resta
solo lo zero.

E' esattamente la riconciliazione che Astra ha prescritto — «riconciliate saldi iniziali,
movimenti e saldi finali» — e che ho fatto a meta': ho riconciliato l'outlier, non la
popolazione.
