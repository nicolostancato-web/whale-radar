> # ⛔ I NUMERI DI QUESTO DOCUMENTO SONO SUPERATI
>
> Tutto cio' che segue e' misurato con la **media**, che su questi mercati e' inservibile: un solo
> token che fa +1.972% sposta la media di 63 pool di quaranta punti. Sei versioni di questo
> documento hanno inseguito quel singolo token credendo di misurare una strategia.
>
> **Il risultato valido e' in [SUCCESSIONE_PATTERN.md](SUCCESSIONE_PATTERN.md)**, misurato sulla
> frequenza dei colpi grossi — che un singolo token non puo' spostare.
>
> Questo file resta come storia degli errori, non come risultato.

# 🔍 Il primo segnale — e la falla che la revisione esterna ha trovato subito

> **AGGIORNAMENTO delle 03:30, dopo la revisione di Astra.** Il risultato descritto sotto era
> **gonfiato da una falla**, e va letto con la correzione in cima. Lascio il testo originale perche'
> serve a vedere quanto fosse convincente prima che qualcuno lo guardasse da fuori.

---

## LA FALLA (trovata da Astra in un colpo solo)

> *«Un quarto della vita osservata puo' incorporare informazione futura. Per individuare il primo
> quarto serve conoscere il futuro.»*

Fissavo il momento della decisione a un quarto della vita **osservata** del pool. Ma la vita
osservata finisce con l'ultimo scambio — un evento **futuro**. Un pool vissuto 24 ore ha la
decisione all'ora 6; uno morto in un'ora ce l'ha a 15 minuti. **Per sapere dove cade «un quarto»
bisogna gia' sapere quando il pool morira'**, e la longevita' e' correlata con tutto il resto.

Astra l'aveva anche indicato come «il singolo controllo che ha maggiore probabilita' di far
crollare il risultato». Aveva ragione.

## IL RISULTATO CORRETTO

Rifatto tutto col momento della decisione fissato a **due ore dal primo scambio osservato** —
uguale per tutti, e noto in quel momento.

| | candidati, versione con la falla | versione onesta |
|---|---|---|
| robinhood | 71 su 114 | **31 su 108** |
| base | 52 su 112 | **23 su 95** |

E il walk-forward, che e' quello che conta:

| | regole che reggono su dati mai visti | mediana | il mercato |
|---|---|---|---|
| **robinhood** | **63/67 = 94%** | +2,2% / +5,1% / +5,5% | +2,1% / −5,9% / −3,7% |
| **base** | **0/5 = 0%** | −13,1% | −10,4% |

**Su robinhood l'effetto sopravvive** — anzi e' piu' COSTANTE di prima (94% contro 70%) — ma molto
piu' **piccolo**: 2-5% in sei ore invece di 6-31%.

**Su base crolla del tutto.** Quello che sembrava un effetto marginale era la falla.

**Lettura onesta: una chain su due, con guadagni modesti ma costanti.** E' molto meno di quanto
sembrasse due ore fa, ed e' probabilmente vero.

## IL RISULTATO DOPO ENTRAMBE LE CORREZIONI (03:40)

Chiusa anche la seconda falla — i pool in cui si entra e da cui non si esce piu' contano come
perdita totale invece di essere scartati (erano l'1,4% su robinhood, il 3,5% su base):

| | candidati, con entrambe le falle chiuse |
|---|---|
| **base** | **ZERO su 79 combinazioni** |
| **robinhood** | 27 su 100 |

**Su base non c'e' niente**, e lo dicono TRE controlli indipendenti: il walk-forward onesto (0
regole su 5), il conteggio dei pool senza uscita (+16,0% -> −1,1%), e il cercatore corretto (zero
candidati). Quello che sembrava un effetto marginale erano due falle sovrapposte.

**Su robinhood resta qualcosa:** il gruppo scelto rende **+12,9%** contro **+5,4%** di un gruppo a
caso preso nelle stesse ore. Circa sette punti di vantaggio, non i quaranta di stanotte.

Le condizioni sono sempre le stesse: **molti compratori distinti e ritmo di scambi alto.**

### La cronologia dei numeri, che vale piu' del numero finale

| momento | cosa dicevo | cosa era |
|---|---|---|
| 01:30 | «+63% di portafoglio» | media gonfiata dalla coda |
| 02:00 | «72% delle regole reggono» | un solo taglio temporale |
| 02:30 | «70%, ma una finestra su cinque no» | piu' onesto, ancora con la falla |
| 03:10 | Astra trova la falla del momento della decisione | |
| 03:25 | «robinhood +2/+5%, base crolla» | mancava ancora la seconda falla |
| 03:40 | **«base zero, robinhood +7 punti sul caso»** | con entrambe chiuse |

Due ore, sei versioni, e ogni versione era piu' piccola della precedente. **Il numero e' sceso ogni
volta che ho guardato meglio** — che e' esattamente cio' che ci si deve aspettare quando si parte da
un risultato viziato, e cio' che NON succede quando si parte da un risultato vero.

Non so ancora se il +7 e' vero. So che e' sopravvissuto a piu' controlli di tutti i numeri
precedenti.

## Cosa resta aperto, dalla stessa revisione

Astra ha sollevato altri otto rilievi che NON ho ancora verificato, e due sono seri:

1. **Il campione e' selezionato dalla possibilita' di misurare l'esito.** Richiedere due ore di
   vita esclude i pool che muoiono prima — cioe' forse le perdite peggiori.
2. **Le regole potrebbero riusare gli stessi pool.** 67 verifiche che vincono grazie agli stessi
   token non sono 67 conferme.
3. **La prova di rimescolamento ha un pavimento.** Con 8 repliche il p-value minimo possibile e'
   1/9 = 11%, non 5%: «zero su otto» e' molto meno forte di come l'avevo presentato.

---

# (testo originale del 23/09 notte, prima della revisione)

# 🔍 Il primo segnale che ha superato tutte le prove

*23 settembre 2026, notte. Scritto mentre i numeri sono buoni, che è il momento in cui storicamente
si sbaglia — quindi con i limiti in fondo e non in una nota a piè di pagina.*

---

## Cosa è stato trovato

Il cercatore ha girato per la prima volta e ha proposto delle **successioni di pattern**: condizioni
osservabili al momento della decisione che precedono un rendimento migliore degli altri token dello
stesso momento.

Le variabili che emergono, **su entrambe le chain indipendentemente**:

- **il ritmo degli scambi** (quanti scambi per ora di vita del pool)
- **il numero di compratori distinti**
- **quanti indirizzi diversi per scambio** (molte persone, non una che si fa volume da sola)

---

## Le cinque prove, in ordine di severità

### 1. Rimescolando gli esiti, la ricerca non trova più niente

La prova più severa: si prendono i dati VERI e si rimescolano solo gli esiti dentro ciascuna ora.
Restano identiche le distribuzioni, i legami, i valori delle condizioni. Sparisce solo il nesso fra
condizioni e risultato.

| | candidati con i dati veri | con gli esiti rimescolati |
|---|---|---|
| base | 21 | **0** su 8 prove |
| robinhood | 66 | 2,8 in media su 6 prove |

Su base: **zero, otto volte su otto.**

### 2. Le stesse variabili su due chain indipendenti

Base e robinhood sono mercati diversi, con nodi diversi e raccolte diverse. Le condizioni che
emergono sono le stesse. Una coincidenza è possibile; due mercati che indicano le stesse tre
variabili lo è meno.

### 3. I guadagni erano incassabili davvero

Il dubbio serio: i rendimenti enormi potevano essere prezzi sulla carta, di pool svuotati dove
nessuno poteva vendere. Verificato sui dieci maggiori: **7-11 indirizzi distinti hanno venduto**
durante la finestra, su 130-220 scambi. Fra tutti i 108 guadagni sopra il +300%, **solo il 2% non
aveva alcun venditore**.

Gente vera stava incassando mentre quei token salivano.

### 4. Il guadagno non si regge su tre fortunati

Sulla regola migliore di robinhood (445 pool):

| | |
|---|---|
| rendimento di portafoglio | +63% |
| **il token tipico (mediana)** | **−5,74%** |
| in guadagno | 37% |
| togliendo i 10 maggiori | **+27,75%** |

La forma è quella giusta per questo mercato — molti perdono, pochi pagano tutto — ma con ampiezza:
togliendone dieci su 445 resta più di un quarto.

### 5. Regge su dati mai visti

Regole cercate sulla PRIMA metà del tempo, misurate sulla SECONDA.

| | regole ancora in guadagno e sopra il mercato | rendimento mediano | il mercato |
|---|---|---|---|
| **robinhood** | **41/57 = 72%** | **+14,5%** | −7,9% |
| base | 23/35 = 66% | +0,3% | −12,2% |

È la prova che uccide la maggior parte dei risultati. Su robinhood non l'ha ucciso.

### 6. Cinque finestre invece di una — e qui il risultato si ridimensiona

Il punto 5 usava UN taglio temporale. Rifatto con cinque finestre consecutive: si cerca su una, si
verifica sulla successiva, si avanza.

| robinhood, da → a | regole che reggono | mediana | il mercato |
|---|---|---|---|
| 1 → 2 | 9/31 = **29%** | **−3,8%** | +3,1% |
| 2 → 3 | 20/43 = 47% | −0,4% | −18,4% |
| 3 → 4 | 38/38 = 100% | +31,1% | +7,7% |
| 4 → 5 | 13/17 = 76% | +6,5% | −8,0% |
| 5 → 6 | 42/45 = 93% | +18,7% | −7,0% |
| **totale** | **122/174 = 70%** | **+6,5%** | |

**L'effetto NON è stabile.** In una finestra su cinque le regole hanno fatto peggio del mercato, e
la dimensione oscilla fra −3,8% e +31,1%.

Il taglio singolo diceva 72% e sembrava solido. Cinque tagli danno 70% — quasi lo stesso numero —
ma mostrano che dietro c'è **una finestra in cui non ha funzionato affatto**. Il taglio singolo lo
nascondeva, e nessuno l'avrebbe mai saputo.

**La lettura onesta cambia:** non «abbiamo un vantaggio», ma **«un effetto presente nella maggior
parte dei periodi, assente in alcuni, di dimensione molto variabile»**. È ancora notevole — 70% su
dati mai visti non è rumore — ma non è una macchina da soldi, ed è esattamente la differenza fra
un'ipotesi che merita di andare avanti e una promessa.

---

## Cosa NON è dimostrato, e sono cose grosse

**1. L'esecuzione è modellata, non provata.** I costi sono dentro (impatto misurato 0,45% mediano,
raddoppiato per prudenza, andata e ritorno) ma non abbiamo mai comprato e venduto davvero. Il caso
documentato altrove — 5,7 milioni persi su 9 perché il prezzo si è mosso durante l'esecuzione — è
esattamente ciò che questa prova non copre.

**2. Una sola divisione temporale.** «Prima metà / seconda metà» è un taglio solo. Tre finestre
dentro lo stesso episodio di mercato sono una finestra guardata tre volte.

**3. Base è marginale.** +0,3% mediano dopo i costi è pareggio. L'effetto c'è — batte un mercato a
−12,2% — ma non paga.

**4. Il momento della decisione è arbitrario.** È fissato a un quarto della vita osservata del pool:
dichiarato e uguale per tutti, ma scelto da noi.

**5. Non è stato ancora visto da nessuno da fuori.** Ogni volta che in questo progetto un risultato
è stato creduto senza revisione esterna, era sbagliato. Tre giorni fa il database era «pronto» e
aveva il 17% di dati errati.

---

## Il prossimo passo, in ordine

1. **Sottoporlo ad Astra** — con i numeri e senza il ragionamento che li ha prodotti, così giudica
   il risultato e non la storia.
2. **Più divisioni temporali**, non una sola.
3. **Registrarlo come ipotesi** in `IPOTESI.md`, con la sua condizione di morte, e confermarlo in
   avanti sulle previsioni che si stanno già accumulando.
4. Solo dopo, e solo se regge tutto: parlare di soldi veri.

**Nessuna di queste è opzionale.** È la prima volta che qualcosa arriva fin qui, e per questo è
anche il momento di massimo pericolo: i numeri piacciono, e quando piacciono si smette di
controllarli.
