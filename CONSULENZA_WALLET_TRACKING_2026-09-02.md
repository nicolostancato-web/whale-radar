# 🧠 CONSULENZA ESTERNA — wallet tracking (02/09/2026)

Consulto su un secondo modello sulla chiusura del copy-trading. Solo l'oro applicabile.

---

## Il verdetto: «giusta, ma per il motivo sbagliato»

Chiudere **"2 successi = wallet bravo"** è corretto. Ma non abbiamo dimostrato che
*qualsiasi* forma di wallet intelligence sia morta — abbiamo dimostrato che *quella
definizione* non funziona.

E il colpo che uccide la strategia non sono i costi: su Base in validazione il segnale
fa **−3% lordo** contro **+2% del caso**. *Prima ancora di pagare qualcosa, non c'è alpha.*

---

## 🔴 LA COSA PIÙ IMPORTANTE — una contraddizione dentro il nostro sistema

> «Non puoi contemporaneamente dire "i costi sono misurati" e poi usare un modello molto
> più severo del dato misurato.»

Ha ragione, ed è verificato:

| | costo andata+ritorno | pareggio |
|---|---|---|
| **Misurato** (Jupiter, $25) | **4,0%** | **~1,04x** |
| **Misurato** (Jupiter, $100) | 8,5% | ~1,09x |
| **Usato nel backtest** | **~33%** | **1,52x** |

Il modello è **8 volte più severo** del dato misurato alla size che ci interessa.
Ogni verdetto "negativo al netto" dato finora poggia su quel 33% assunto — incluso
"tutte e quattro le chain sono negative".

**Ma attenzione, in entrambe le direzioni:** il 4% è misurato su **5 token**, e uno dei
cinque era **invendibile**. Nessuno dei due numeri è ancora affidabile. La distinzione
giusta non è "il costo è alto o basso": è che **invendibile non è un costo alto, è una
perdita totale** — e va contata a parte, non spalmata sulla media.

### Fatto oggi
- `costi_reali.py` ora **accumula** invece di riscrivere (prima ogni giro azzerava a ~5 token)
- agganciato al ciclo del motore ogni ~2h, 25 token per giro → l'archivio cresce da solo
- il verbale separa **% invendibili** dal **costo sui vendibili**

---

## Gli errori del nostro test, in ordine di gravità

1. **Costi incoerenti** (sopra) — in lavorazione.
2. **"2 successi" non misura bravura.** Su decine di migliaia di wallet, molti azzeccano
   due volte per puro caso. La definizione giusta: *quanto ha fatto meglio di token
   comparabili comprati negli stessi momenti*, con **shrinkage** — pochi casi = punteggio
   vicino a zero. Servono **20-30 token distinti**, soglia fissata **prima** di guardare i dati.
3. **Il controllo "compra a caso" è grezzo.** Va appaiato per età, liquidità, chain,
   vendibilità, costo di uscita. La domanda giusta non è *«il wallet batte un token a caso?»*
   ma *«a parità di opportunità disponibili in quel momento, il suo acquisto aggiunge informazione?»*
4. **Pseudo-replicazione.** 32.749 acquisti BSC non sono 32.749 esperimenti: stesso wallet,
   stesso token, stesso cluster, stesso creator. L'unità giusta è
   **prima decisione (cluster × token)**.
5. **Le 24h fisse potrebbero uccidere un segnale vero.** Un wallet può avere informazione
   che vale 30 minuti. Da misurare a orizzonti fissati prima: 5m / 30m / 2h / 6h / 24h.
6. **Survivorship bias sui wallet:** vediamo i loro acquisti solo dove incrociano il nostro
   universo. I loro fallimenti fuori dal database mancano → fabbrichiamo "wallet bravi".

> Nota utile: 218 casi sono pochi per dire *"questa strategia guadagna"*, ma sono
> **molto informativi** per dire *"il +24% non si replica"*. Da +24% a −3% è un crollo.

---

## Le 3 piste da testare adesso (ordinate)

### 1. Reputazione del creator + vendibilità ⬅️ la più difendibile
**Perché:** un grafico non causa un rug, **una persona sì.** Non cerchiamo una correlazione
magica: identifichiamo la controparte che controlla il gioco. Abbiamo già il grafo dei creator.
**Come:** al tempo T solo la storia precedente del creator; confronto fra creator puliti e
problematici appaiati per età/chain/liquidità. Misura: probabilità di diventare invendibile,
perdita estrema, sopravvivenza, CVaR. Usarlo come **cancello**, non come predittore di rendimento.
**Morte:** se su due coorti future non riduce gli eventi terminali, o scarta così tanto da non
migliorare il P&L per token eleggibile → stop.

### 2. Flusso di ordini dei *cluster*, non "wallet bravo"
**Perché:** 30 wallet diversi finanziati dallo stesso portafoglio non sono 30 compratori: è
**una entità sola**. Se invece cresce il capitale di compratori *davvero indipendenti* rapportato
alla liquidità, può esserci domanda vera non ancora nel prezzo. È microstruttura, non superstizione.
**Come:** segnale calcolato solo fino a T, escludendo creator e wallet collegati; excess return
a 5m/30m/2h/6h contro controlli appaiati. **Placebo all'indietro**: se il segnale "predice" anche
ciò che è già successo prima di T, è leakage o momentum già avvenuto.
**Morte:** nessun excess return stabile dopo T, o sparisce entro il nostro ritardo reale → chiudi.

### 3. Sopravvivenza + evento di domanda
Non "compra a 30 minuti di età": aspetta un **evento** su un token che ha passato sicurezza,
è vendibile, ha costo di uscita sotto soglia, non ha perso liquidità, e mostra domanda netta
distribuita. **Morte:** se il cancello migliora solo la perdita media ma il segnale di domanda
non produce excess return → non c'è strategia direzionale.

> ⚠️ **«Non chiamare edge una macchina che passa da −40% a −10%.»**

---

## La domanda scomoda

> «Con un vero pareggio a +50%, io cambierei mercato.»

Ma con un caveat che ci riguarda direttamente: **non è detto che il nostro pareggio vero sia
+50%.** Se il costo reale a $25 è ~4% all-in, un segnale da +10-15% di excess return diventa
economicamente interessante. Se invece, contati tax, fallimenti, MEV, gas e route che spariscono,
il costo effettivo torna al 30-50% → allora sì, abbandonare i token appena nati e guardare
mercati più liquidi, orizzonti più lunghi, o **vendere l'intelligence di rischio invece di
prendersi il rischio**.

**Tutto passa da lì. Per questo la riconciliazione dei costi viene prima di ogni altro test.**

---

## La cosa che ci stavamo perdendo

Stiamo cercando di rispondere con **un'unica domanda** ("quanto rende questo token").
Vanno separate in **tre macchine**:

| | domanda | dati |
|---|---|---|
| **1** | posso uscirne? → P(vendibile fra H) | sicurezza, creator, liquidità |
| **2** | se sopravvive, ha upside? *(solo sui token che passano 1)* | flusso ordini, cluster, prezzo, volume |
| **3** | vale la pena? probabilità × payoff − costo reale | può rispondere **SKIP** |

Un ottimo rilevatore di rug non deve per forza saper prevedere i vincitori.

---

## Conclusione operativa

- ❌ Chiuso: **"2 winner = wallet bravo"**
- ⏸️ Non ancora chiusa: **wallet intelligence** — le spetta un ultimo test con skill
  appaiata e shrinkata, **prima ignorando i costi** (esiste informazione? sì/no)
- 🥇 Priorità assoluta: **riconciliare il modello dei costi** — finché non è coerente,
  ogni verdetto netto, positivo o negativo, è contaminato
- 🥈 Poi: **creator risk** e **order flow di cluster**, le due piste più difendibili
  con il database che possediamo
