# ⚖️ DECISIONE: l'embargo diventa una proprietà della fonte

*15 settembre 2026 · decisione delegata da Nicolò · applicata, con il vecchio metro congelato*

## Cosa c'era

Una regola sola per tutto: **35,4 ore**. Per decidere a un certo istante, si potevano usare solo dati
più vecchi di 35 ore.

Nasceva da una misura vera — quanto tardi i fornitori ci consegnano i dati — ma prendeva **il
peggiore fra le chain**. E il peggiore era **BSC: una chain abbandonata il 9 settembre**.

> Una chain morta decideva per tutte le altre.

**Conseguenza misurata**: l'entrata è a +3h dalla nascita del token, quindi il sistema cercava dati
di **32 ore prima che il token esistesse**. Il 92% delle righe aveva le variabili sugli scambi vuote.

## Cosa c'è adesso

L'embargo non è più un numero: è **una proprietà del singolo dato**, che dipende da **dove arriva**.

| fonte | quanto deve aspettare | perché |
|---|---|---|
| fornitori (API), base | **10,8 h** | il ritardo misurato di *quella* chain |
| fornitori, solana | 16,6 h | idem |
| fornitori, robinhood | 4,0 h | idem |
| **catena, letta da noi** | **30 minuti** | il tempo che impieghiamo a leggerla |
| ~~bsc~~ | esclusa | abbandonata, non decide più per nessuno |

## Perché 30 minuti e non zero

Zero sarebbe la risposta comoda, e sarebbe falsa: significherebbe sostenere di conoscere un blocco
**nell'istante in cui nasce**. Non è vero — lo conosciamo quando il nostro collettore passa di lì.

Mezz'ora è **più lento di quanto facciamo davvero**. Se sbagliamo, sbagliamo per prudenza.

> Un embargo troppo stretto costa occasioni. Uno troppo largo costa soldi veri.

## L'effetto, misurato

| chain | righe utilizzabili, metro vecchio | metro nuovo |
|---|---|---|
| base | 31 su 400 (**8%**) | **224 su 400 (56%)** |
| robinhood | 27 su 400 (**7%**) | **230 su 400 (57%)** |

**Da 8% a 56%.** Non perché abbiamo abbassato l'asticella: perché abbiamo smesso di chiedere a un
dato che abbiamo in mano di aspettare il ritardo di una chain che non usiamo più.

## La protezione, che è la parte importante

**Il passato non è stato riscritto.**

- il metro vecchio (35,4h per tutto) resta congelato, com'era
- il metro nuovo nasce **accanto**, con il suo nome: `v2-per-fonte`
- ogni risultato dichiara con quale metro è stato misurato
- **mai un confronto fra numeri di metri diversi**

Non è una correzione della storia. È **un secondo strumento, dichiarato**.

## Cosa NON cambia

Il test che conta resta **identico**: la permutazione a blocchi che ha ucciso la classe povera.
Nessuno sconto, nessuna versione più gentile. Se le variabili nuove non battono il massimo del caso,
muoiono come le altre.

**Una scatola più grande non rende più probabile che l'edge esista. Rende possibile accorgersene, se
esiste — e anche più facile illudersi.** Per questo il giudice non si tocca.
