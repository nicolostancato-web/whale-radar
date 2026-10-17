# Entrare primi non paga — 6 ottobre 2026, 17:30

## La risposta alla domanda di Nicolò

*«Dobbiamo capire se c'è gente che entra all'inizio all'inizio e fa tante X.»*

**No, non sul conto onesto.** E il primo arrivato è il **peggiore** di tutti.

| posizione in fila | solo chi ha venduto | quota che non vende mai | **conto onesto** |
|---|---|---|---|
| **1°** | 1,2063x | **39,5%** | **0,8540x** |
| 2° | 1,0607x | 20,3% | 0,9378x |
| 3° | 1,0352x | 23,1% | 0,9480x |
| 10° | 0,9568x | 19,4% | 0,9208x |
| 50° | 0,8882x | 19,5% | 0,8712x |

**98.025 casi in prima posizione. Nessuna selezione.** E il gas non è ancora incluso, quindi la
colonna di destra è un limite superiore.

## Com'è andata, passo per passo — perché il percorso conta più del numero

**Primo numero: +20,6% per chi entra primo.** Ritorno sul capitale, 98.000 casi, gradiente
monotono fino a −11% per il cinquantesimo. Sembrava il risultato più forte mai prodotto dal
progetto.

**Controllo 1 — lo decide un caso solo?** No. Togliendo il più grosso: 1,2063 → 1,2065. Togliendo
i primi dieci: 1,2092. Il singolo più grosso pesa lo **0,1%**. Il risultato era diffuso.

**Controllo 2 — è il nostro campione di «vincenti scelti da noi»?** No: **98.012 casi su 98.025**
sono portafogli qualunque, con il giro completo sulla curva. Zero selezione.

**Controllo 3 — e chi ha comprato e non ha mai venduto?** **Qui il segno si è ribaltato.** Il
39,5% dei primi arrivati **non vende mai**: comprano anche le monete che muoiono nello stesso
minuto. Contando quelle come perdita totale — che è quello che sono — il +20,6% diventa **−14,6%**.

**Controllo 4 — non è che sono solo posizioni aperte da poco?** No. Contando come perdita solo
ciò che è fermo da oltre 1, 3 o 7 giorni, il risultato non si muove: 0,857x / 0,863x / 0,883x. Le
posizioni «ancora aperte» sono meno dell'1%.

## Perché il primo arrivato è il peggiore

Non è un paradosso: è selezione al contrario. Chi compra per primo compra **prima di sapere se la
moneta vivrà**. Chi compra decimo ha già visto nove persone entrare — un'informazione che il primo
non ha. Il vantaggio di prezzo del primo (compra 1,26 volte più gettoni per unità di valuta del
decimo, misurato) **non copre** il fatto che compra più spesso una moneta morta.

## La lezione, che è la stessa di sempre in un posto nuovo

Avevo in mano un **+20,6% su 98.000 casi, robusto agli estremi e senza selezione**. Tre controlli
su quattro lo confermavano. Il quarto — *«e quelli che non hanno mai venduto?»* — l'ha ribaltato.

È la lezione del **fondale onesto**, già scritta in questo progetto il 5 ottobre: *una posizione
senza uscita misurabile vale −100%, non «non misurabile»*. Oggi l'ho riapplicata in un posto nuovo
e ha cambiato il segno della risposta.

**Se mi fossi fermato al terzo controllo avrei detto a Nicolò «entrare primi rende il 21%».**
Sarebbe stato il numero più convincente e più sbagliato della giornata.

## Cosa resta vivo

- **Il 2° e il 3° sono i meno peggio** (0,94-0,95x) e hanno la coda migliore (1,7% e 1,5% sopra
  10x contro lo 0,3% del primo). Se c'è qualcosa, è lì — non in prima fila.
- **Il gas non è incluso.** Va aggiunto: può solo peggiorare questi numeri, mai migliorarli.
- **Questo misura il giro che comincia e finisce sulla curva.** Chi gradua e vende nel pool è
  ancora da misurare su larga scala: oggi quei casi erano meno di 50.
- Il vantaggio di prezzo del primo arrivato è reale e misurato (1,26x di gettoni in più del
  decimo). Non basta, ma è un fatto su cui si può costruire una domanda diversa.

## Dove si guarda

`agents/x_di_chi_entra_prima.py`, collegato alla corsia `curva_lanci`. Il conto onesto va
aggiunto all'agente: oggi l'ho fatto a mano, e una misura fatta a mano è una misura che si perde.
