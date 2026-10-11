# ⚠️ DIFETTO NOTO — l'orario dei record della coda viva raccolti prima del 16/09 ore 09:00

**Cosa c'è di sbagliato.** Ogni record in `data/multichain/*/vivo/` raccolto prima di quel momento
porta un campo `ts` **fino a 32 minuti più vecchio del vero**.

**Perché.** L'istante di ogni scambio veniva interpolato a partire da un punto di riferimento
(blocco di punta + ora) preso una volta sola, all'**avvio** del giro. Quel riferimento invecchia
insieme al giro: dopo un'ora di lavoro, i blocchi appena presi risultavano vecchi di mezz'ora.

**Misurato, non stimato** (16/09, blocco base 51375279):

| | valore |
|---|---|
| istante scritto da noi | 1789538007 |
| istante vero della catena | 1789539905 |
| **errore** | **−31,6 minuti** |

**Le due conseguenze, e la seconda è la peggiore.**

1. Il ritardo sembrava 21 minuti quando il vero era **zero**: la coda viva funzionava benissimo e
   noi la stavamo giudicando rotta. Il 62% dei record è stato declassato a `ricostruzione-storica`
   pur essendo point-in-time perfetti.
2. Il campo `ts` è l'orario su cui poggiano l'embargo, le unioni e ogni analisi futura. Un ritardo
   sbagliato è un indicatore sbagliato; **un orario sbagliato è un dato sbagliato**, e si propaga a
   tutto quello che ci costruisci sopra.

**Cosa NON è sbagliato.** Il campo `blocco` è esatto — viene dalla catena, non da un calcolo. Anche
`tx`, `li`, `bh`, `acq` e le quantità sono esatti.

**Quindi l'orario si può ricostruire**, quando servirà, chiedendo alla catena l'istante vero di quei
blocchi. Finché non è fatto: **per i record vivo precedenti al 16/09 ore 09:00, non fidarsi di `ts`
né di `classe`; usare `blocco`.**

**Riparato il 16/09.** Adesso si chiedono alla catena gli istanti veri dei due estremi di ogni lotto
e si interpola solo dentro quei due — poche centinaia di blocchi invece di milioni. Verificato dopo
la correzione: **errore 0 secondi**.

---

*Perché questo documento esiste: un difetto noto e scritto costa un'ora di lavoro domani. Un difetto
noto e taciuto costa una conclusione sbagliata fra tre settimane, quando nessuno si ricorda più
perché quei numeri non tornavano.*
