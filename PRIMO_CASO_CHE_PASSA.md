# Il primo caso che passa i tre requisiti — e chi c'è dietro

7 ottobre 2026, sera.

## Il caso

| | |
|---|---|
| portafoglio | `0xfebcbc0a8b2a1819be1f1696895f13e7ae65479a` |
| moneta | `0x22bb10e3e1e932b03bef90bb1cf7305d896c55bb` |
| speso | 0,111625 ETH ≈ **287 $** |
| incassato | 0,563194 ETH ≈ **1.451 $** |
| risultato | **5,05x**, gas incluso |
| acquisto | `0xc7756ad9e78c05096018d3d5dc80b7e62d0edffe75bd6d8fbba03a40f352ee00` |
| vendite | `0x48ec34b9…`, `0xaa1d0f98…`, `0x5359739
9…` |

Verificato per tre strade diverse: ricalcolo indipendente dalla chain (combacia), lettura delle
ricevute delle singole transazioni (0,11162505 contro 0,111625 dichiarato), gettoni venduti uguali
a quelli comprati. Posizione **intera**: letta dal blocco di nascita della moneta.

## La scoperta che conta più del caso

La ricevuta dell'acquisto contiene **9 CurveBuy a 9 portafogli diversi**: una sola transazione che
compra per nove portafogli insieme. E chi la firma — `0x1793de06fd…` — è a sua volta nella mia
classifica, a 4,10x.

Quindi i «nove vincenti» non sono nove persone brave: sono **una decisione sola**. Sul totale il
fenomeno è raro (12 portafogli su 1.594, lo 0,8%), ma **in cima pesa**: 6 delle 31 posizioni sopra
2x vengono da quel singolo grappolo, il 19%.

**Regola nuova, scritta nel codice: i portafogli che comprano nella stessa transazione contano
come uno.** Senza questa, una classifica di «chi fa più X» è in parte la stessa persona contata
nove volte.

## Un difetto nel mio cancello, trovato qui

`prima_la_prova.py` leggeva solo gli scambi nei pool (Uniswap v2/v3/v4). Su un acquisto sulla
curva rispondeva **«NON TROVATA»**, che si legge come «la transazione non esiste» e invece voleva
dire «non la so leggere». Un falso negativo: il mio stesso peccato al contrario — un'ignoranza
travestita da fatto. Bocciava un caso sano. Ora legge anche la curva.

## Il quadro onesto, su 2.216 posizioni intere e sane

| | |
|---|---|
| mediana | **0,812x** — la maggioranza perde |
| sopra 2x | 31 su 2.216 (**1,4%**) |
| sopra 5x | **1** |
| sopra 10x | **0** |

Le 31 sopra 2x sono su 14 monete distinte, e una moneta sola ne fa 6.

**Il 10x che cerchiamo, qui dentro, non c'è.** Questo campione è la curva *prima* della
quotazione: 465 monete lette per intero. Se le X grosse esistono, stanno dopo — nel pool — ed è
esattamente la misura che ho ritirato stamattina perché costruita su file contaminati. Si rifà
sui dati nuovi.
