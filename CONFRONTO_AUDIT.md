# ⚔️ CONFRONTO AVVERSARIALE SULL'AUDIT

*13/09/2026 · Claude propone, il revisore esterno demolisce, Claude risponde · nessun consenso
considerato prova*

---

## COSA È STATO DEMOLITO

### ❌ Un errore di fatto, e me l'ha preso subito

Ho riportato i tentativi di **BSC** — una chain che abbiamo **abbandonato** — accanto a Base e
Solana, come se fosse una delle tre attive. Verificato nei file di stato:

| file | chain | tentativi |
|---|---|---|
| explorer_base | base | 1.958.455 |
| explorer_solana | solana | 951.143 |
| explorer_bsc | **bsc (abbandonata)** | 262.113 |
| explorer_rh + explorer_robinhood | robinhood | 94.562 + 1.181 |

**Robinhood ha fatto 95.743 tentativi, non 262.113.** Il numero di Base regge, ma avevo messo in
tabella una chain che non gareggia più. Correzione accettata.

E ho confuso **+8% (obiettivo operativo)** con **+10% netto (il cancello pre-registrato)**. Sono due
numeri diversi e vanno tenuti separati.

### ❌ TESI 2 — «il migliore è rumore selezionato»: **plausibile, ma NON dimostrata**

La critica è corretta e precisa: *1.958.455 tentativi non sono 1.958.455 confronti indipendenti*.
Potrebbero essere cinque passaggi sugli stessi dati, o cinque finestre mobili, o cinque semi
diversi — sono problemi statistici **diversi**, e il nostro registro non permette di distinguerli:
non salviamo `config_hash`, `dataset_hash`, taglio temporale, seme.

E il mio «8 punti ≈ due errori standard» è **non giudicabile**: errore standard *di cosa*? Per
token, per trade, per giorno, per gruppo? Senza quello, quella soglia non ha significato
inferenziale. **Accetto: era una frase che suonava rigorosa e non lo era.**

### ❌ TESI 4 — il test del segnale iniettato: **invalido nella forma che avevo proposto**

Il colpo più duro, e ha ragione su entrambi i lati:

- **Se fallisce** non dimostra niente: la pipeline non costruisce feature da eventi grezzi, quindi
  fallire è *previsto per architettura*. Dimostra solo che non ha un generatore di feature sui
  wallet — cosa che sapevo già leggendo il codice.
- **Se riesce** è ambiguo: potrebbe averlo trovato tramite un **proxy** già presente (numero di
  compratori, volume iniziale, liquidità), senza aver scoperto niente.

Il test va rifatto a **quattro bracci**: segnale definito al taglio d'entrata, reso ortogonale alle
dieci feature esistenti stratificando, un **oracolo** che riceve il segnale direttamente (se non lo
trova nemmeno l'oracolo, il problema è la potenza statistica e non c'è verdetto), e controlli con
segnale permutato. Solo la combinazione «l'oracolo lo trova, la pipeline no, e sparisce togliendo
l'informazione sui wallet» dimostra qualcosa.

---

## COSA È RIMASTO IN PIEDI

### ✅ TESI 1, ma in forma più precisa di come l'avevo scritta

Il revisore raffina, e la sua versione è migliore della mia: la regressione è additiva, **ma la
strategia complessiva no** — soglia, ora d'entrata, stop, trailing e due take profit interagiscono
in modo fortemente non lineare nel risultato realizzato. Quindi la pipeline **può** scoprire che una
combinazione di feature esistenti e regole d'esecuzione funziona fuori campione.

Il limite vero, riformulato: **la classe di ipotesi non contiene identità e relazioni fra wallet,
sequenze di scambi, dinamiche dentro la finestra.** Non può scoprire un segnale che richieda quelle
variabili. Non segue che non possa scoprire nulla.

> Questa è una tesi più debole della mia — e più difendibile. La adotto.

### ✅ TESI 3, ma senza il salto che ci avevo appoggiato sopra

Che `wallet_scores.json` non sia letto da nessun modello è **verificato**. Ma il revisore ha ragione
su tre salti logici che avevo fatto:

1. 9.743 punteggi salvati **non implicano** che siano predittivi — e se sono calcolati con
   operazioni **successive** al token analizzato, introdurli sarebbe **fuga di informazione**, non
   miglioramento.
2. «un wallet appare su tre nostri token» non è un segnale: può essere un bot, un launchpad, un
   periodo di euforia, o semplice selezione postuma dei "token nostri".
3. Dire che la sequenza è «buttata via» è impreciso: le feature da candele possono contenerne una
   traccia indiretta. **Verificabile è invece che il modello non distingue** vendite-prima-di-acquisti
   da acquisti-prima-di-vendite, tre acquisti dallo stesso wallet da tre di wallet diversi, raffiche
   da scambi distanziati. `sell_ratio` collassa tutte queste storie in un numero solo.

**È un limite rappresentazionale reale. Non è una prova che lì dentro ci sia del valore.**

---

## LA COSA CHE NON AVEVO CONSIDERATO

> *Come si distingue «cerchiamo nel posto sbagliato» da «non c'è niente da trovare»?*

Non con un'opinione né con un backtest. La risposta del revisore è la parte più utile di tutto lo
scambio: si definisce una **classe esplicita di strategie** (feature attuali + sequenze + relazioni
wallet-token + liquidità eseguibile + interazioni), e si calcola un **limite superiore simultaneo**
sul rendimento netto di **ogni** membro della classe, con bootstrap a blocchi.

Se il limite superiore del migliore sta **sotto il cancello**, allora si può dire — e solo allora:

> «Nei dati disponibili, con questo universo, questi costi e questa esecuzione, non c'è evidenza che
> una strategia di questa classe raggiunga il cancello.»

E **non** si può dire «non esiste alcun segnale»: potrebbe vivere in dati che non raccogliamo o a
una granularità che non abbiamo.

---

## LA MISURA MANCANTE PIÙ GRAVE

> **La probabilità che l'uscita fosse davvero eseguibile al prezzo simulato, operazione per
> operazione.**

Per ogni take profit, trailing e stop: alla taglia reale, dopo commissioni, gas, tasse del token,
slippage e liquidità *contemporanea*, quell'uscita sarebbe stata eseguita a quel prezzo?

Senza questa misura, **«+10% netto» può essere una proprietà dei nostri OHLC e non di una strategia
eseguibile.** È il tipo di errore che non si vede mai in un backtest e si paga tutto dal vivo.

E ne aggiunge uno che avevo sottovalutato: in una candela che tocca **sia** lo stop **sia** il take
profit, l'ordine dei due eventi è ignoto — serve una regola pessimistica o dati al livello del
singolo scambio.

---

## COSA FACCIO ADESSO, IN ORDINE

1. **Il test di permutazione a blocchi sull'intera pipeline** — non sul solo risultato finale:
   permutare gli esiti **dentro i blocchi** (giornata di lancio), preservando la struttura temporale,
   rieseguire **tutta** la selezione, e confrontare il migliore reale con la distribuzione del
   **massimo** sotto ipotesi nulla. È il test che il revisore indica e che avevo iniziato a costruire
   nella forma sbagliata (permutavo le righe senza blocchi e rieseguivo solo la soglia).
2. **Il registro dei tentativi** con `config_hash`, `dataset_hash`, taglio temporale e seme: senza,
   la tesi 2 resta non giudicabile per sempre.
3. **La misura di eseguibilità delle uscite**, trade per trade.

Nessuna di queste è una strategia. Sono tre strumenti per capire se i numeri che leggiamo
significano qualcosa — e vengono prima di qualsiasi idea nuova.

---

## STATO FINALE DELLE QUATTRO TESI

| tesi | esito |
|---|---|
| 1 — ottimizzatore, non motore di scoperta | ✅ **in piedi, ma indebolita**: il limite è la classe di ipotesi, non l'additività |
| 2 — il migliore è rumore selezionato | ❌ **non dimostrata**. Serve la permutazione a blocchi |
| 3 — dati costruiti e mai usati | ✅ **verificata come fatto**, ❌ **il salto "quindi c'è valore" cade** |
| 4 — test del segnale iniettato | ❌ **invalido come proposto**, va rifatto a quattro bracci |

**Nessun consenso è stato considerato prova.** Due tesi su quattro sono cadute, e la più importante
— che stiamo ottimizzando invece di scoprire — resta **plausibile e non ancora dimostrata**.
