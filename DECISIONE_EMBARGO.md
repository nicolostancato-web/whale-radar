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

---

# CORREZIONE (stesso giorno, dopo la revisione avversariale)

La decisione qui sopra era **troppo generosa**, e il revisore l'ha smontata in una riga:

> «`acq` dimostra che quei dati sono entrati **adesso**, settimane dopo il blocco. Non prova che
> fossero disponibili dopo 30 minuti: **per quei record prova il contrario**.»

## Le tre cose che confondevo

| | cosa dimostra |
|---|---|
| disponibilità **fisica** | un nodo oggi può servire quel log |
| disponibilità **del nodo** | il nodo lo avrebbe servito allora |
| **disponibilità operativa** | **noi sapevamo che quel pool esisteva e lo stavamo interrogando** |

**Solo la terza conta**, e io stavo usando la prima.

Non si può leggere la storia di un pool di cui non si conosce l'esistenza. Se l'abbiamo scoperto
dieci ore dopo la nascita — perché ce l'ha detto un fornitore, col suo ritardo — allora i suoi primi
scambi **non erano nostri** prima di quel momento, per quanto la catena li conservasse.

## La regola corretta

Un dato è disponibile dal **più tardi** fra:

- quando è successo
- **quando abbiamo saputo che quel pool esisteva**

più il tempo che impieghiamo a leggerlo.

## L'effetto, misurato

| chain | metro vecchio (35,4h) | metro troppo generoso | **metro onesto** |
|---|---|---|---|
| base | 8% | 56% | **35%** |
| robinhood | 7% | 57% | **52%** |

**Ho perso 21 punti su Base** rispetto alla versione che avevo appena scritto. Sono punti che non
avevo diritto di avere.

## E l'etichetta che mancava

Lo storico raccolto all'indietro **non è certificato point-in-time**: è **ricostruzione storica**.
Che oggi sia recuperabile non dimostra che allora fosse nostro. Va marcato per quello che è, e il
revisore ha ragione anche su questo: `acq` è buona provenienza, **non risolve il problema**.
