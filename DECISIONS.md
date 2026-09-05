# 🧭 DECISIONS — registro decisioni (append-only, mai cancellare)
> Formato: Data · Problema · Decisione · Alternativa scartata · Esito.

## 2026-09-04 · Il ritardo con cui i dati arrivano DA NOI entra nel metro
- **Problema (dalla revisione esterna):** le feature erano gia' oneste sul passato — verificato
  ricalcolandole senza i dati futuri, e vengono **identiche**. Ma essere oneste non basta: un bot
  vero non puo' decidere su una candela che non ha ancora scaricato.
- **Misura:** il ritardo della nostra catena e' di **3-7 ore** (base 193 min, bsc 336, solana 431,
  robinhood 428), letto sulla coda bassa della distribuzione — la mediana direbbe 58 ore, ma quelli
  sono token MORTI e misurando cosi' la loro morte diventerebbe un difetto nostro.
- **Decisione:** trade e candele si tagliano a `entrata - ritardo`, in entrambe le pipeline di
  feature (multichain e Robinhood). `RITARDO=0` disattiva il taglio per poter confrontare i due mondi.
  Nel dubbio si usa il ritardo **peggiore** fra le chain: sbagliare per prudenza costa occasioni
  perse, sbagliare per ottimismo costa soldi.
- **Effetto misurato:** base -7,6% -> **-7,8%**, bsc -21,0% -> **-23,2%**.
- **Nota su un errore mio:** al primo tentativo il ritardo non cambiava niente, e stavo per
  dichiararlo "applicato". Non lo era: ci sono **due** pipeline di feature e ne avevo toccata una.
  Un cambiamento che non cambia nessun numero non e' una conferma che non serviva — e' il primo
  posto dove andare a controllare.
- **Cosa implica, ed e' la parte seria:** entriamo 3-6 ore dopo il listing, ma con 3-7 ore di ritardo
  un bot vero avrebbe in mano quasi solo i dati del listing. Non e' la stessa strategia con un
  handicap: e' una strategia diversa, e da oggi la misuriamo per quella che e'.
- **Esito:** metro completo. Non restano piu' numeri assunti al suo interno.

## 2026-09-04 · Cancello dei creator: CHIUSO (il criterio scritto prima ha fatto il suo lavoro)
- **Cos'era:** la pista che la consulenza metteva al primo posto — *«un grafico non causa un rug, una
  persona si»*. Il 3/9, su Base con pochi dati, sembrava forte: **91% di disastri fra i creator
  marchiati contro 57% fra i puliti**, 33 punti di differenza.
- **Cos'e' successo:** i dati sono cresciuti. Su un campione di **840 creator puliti contro 73
  marchiati**, la differenza e' scesa a **8 punti** (65% contro 73%).
- **Decisione:** chiusa. Il criterio di morte era scritto il 3/9, PRIMA di vedere questi numeri:
  *«se il cancello non separa in modo apprezzabile, la pista si chiude — non si inventano nuove
  categorie di creator per salvarla»*.
- **Cosa NON facciamo, ed e' il punto:** 73 marchiati sono pochi, e 8 punti potrebbero essere un
  segnale debole vero. La tentazione di dire "aspettiamo ancora un po'" e' esattamente il motivo per
  cui il criterio era stato scritto in anticipo. **Spostare il traguardo dopo aver visto il risultato
  e' il modo in cui un progetto di ricerca diventa una ricerca di conferme.**
- **Cosa resta:** il marchio del creator continua a essere raccolto e resta nel database. Non lo
  usiamo come cancello finche' non arriva un'evidenza nuova, non finche' non troviamo un modo di
  tagliare i dati che lo faccia sembrare migliore.
- **Esito:** nessuna pista viva. Il 33% -> 91% di due giorni fa era rumore di campione piccolo.

## 2026-09-03 · Criteri di STOP scritti PRIMA dei risultati (data/criteri.json)
- **Problema:** il rischio piu' grande non e' sbagliare una strategia. E' continuare ad aggiungere
  segnali, parametri e test finche' prima o poi qualcosa appare verde **per caso**. Con abbastanza
  tentativi si trova sempre qualcosa: non e' un edge, e' rumore che ha vinto la lotteria.
- **Decisione (03/09, su indicazione della consulenza esterna):** scrivere **adesso**, prima di vedere
  altri numeri, cosa significa riuscire e cosa significa fallire. In `data/criteri.json`, leggibile dal
  codice — cosi' se un giorno volessimo abbassare l'asticella, la modifica sarebbe **visibile qui**
  invece che nascosta in un ragionamento.
  - **RIUSCITO** (tutte insieme): rendimento netto **≥ +10%**, **t ≥ 2**, almeno **250 trade**,
    configurazione **congelata prima**, holdout mai visto e letto **una volta sola**, costi condizionati
    alla liquidita' all'uscita.
  - **CHIUSO**: se al **03/10/2026** (o a 500 trade accumulati in validazione) nessuna pista ha superato
    quei criteri. Non significa "il progetto e' fallito", significa **"questo mercato non offre un edge
    sfruttabile con il nostro approccio"** — che e' un risultato, non una sconfitta: dice dove non cercare.
- **Divieti in vigore:** vietato riottimizzare dopo il congelamento; vietato leggere l'holdout piu' di
  una volta; vietato allargare un filtro che non generalizza; vietato aprire una pista nuova mentre una
  vecchia aspetta il verdetto; vietato spostare queste soglie senza scriverlo qui con data e motivo.
- **Applicato subito:** congelata la configurazione Robinhood (+3,5% in ricerca, migliore di ~39
  tentativi). `explorer_rh.py` ora **si rifiuta di girare** su una chain congelata.
- **Esito:** in attesa.

## 2026-09-03 · Il costo si MISURA, non si assume (metro.py)
- **Problema:** dicevamo "i costi li abbiamo misurati" e poi nei conti ne usavamo un altro.
  Misurato su Jupiter (212 token): **4,0%** di andata e ritorno a $25. Usato nel backtest: **~33%**.
  Otto volte piu' severo. Con quel 33% un token doveva fare **+50% solo per pareggiare**, e con quel
  metro avevamo dichiarato morte quattro chain e diverse strategie.
- **Decisione (investitore, 03/09):** il costo misurato diventa il metro **primario**; il vecchio 33%
  resta come **stress test** (`METRO=stress`), non come verita'. Unico posto: `agents/metro.py`.
  Pareggio: da **1,52x** a **1,16x**.
- **Alternativa scartata:** abbassare semplicemente il 33% al 4%. Sbagliato: *si puo' uscire?* e
  *quanto costa uscire?* sono due domande diverse. Le **trappole** (9% dei token a $25: nessuna
  uscita, o uscita che restituisce nulla) sono una **perdita totale**, non una percentuale, e restano
  contate a parte in `COSTO_MODELLO.md`. Spalmarle sul costo medio e' esattamente l'errore del 33%:
  punisce ogni trade con un pezzo del disastro altrui e insieme sottostima il disastro vero.
- **Effetto immediato sui verdetti (stesso codice, stessi dati, solo il metro cambia):**

  | chain | col vecchio 33% | col costo misurato |
  |---|---|---|
  | robinhood | -20,9% | **+5,3%** ⬅ cambia segno |
  | base | -27,2% | -8,5% |
  | solana | ~-31% | -31,0% |
  | bsc | ~-31% | -30,8% |

- **Cosa NON conclude:** +5,3% e' la MIGLIORE di 33 configurazioni provate. E' dentro il rumore da
  selezione. **Non e' un edge finche' il Giudice non lo conferma sulla fascia mai vista.** Il metro
  giusto non crea un vantaggio: smette solo di nasconderne uno eventuale.
- **Esito:** da verificare in validazione.


## 2026-08-07 · Chain target: Robinhood (non Solana)
- **Problema:** su Solana seguivamo "whale" che erano bot-wash da $6. Nessun edge (provato: causal replay + forward study su 39k eventi).
- **Decisione:** spostarsi su **chain Robinhood** (EVM), dove le whale sono VERE (wallet $360k, token $53M, holder $300k-1M — verificato on-chain).
- **Alternativa scartata:** insistere su Solana / forex-BTC (mercati efficienti, retail perde).
- **Esito:** backtest Robinhood mostra aspettativa positiva (vedi EXPERIMENTS).

## 2026-08-07 · Storage: file compressi committati (no database ora)
- **Problema:** dove accumulare i dati gratis, poco spazio, per sempre?
- **Decisione:** file **.jsonl.gz compressi immutabili**, committati nel repo. Query con DuckDB. NO database.
- **Perché committati (non gitignore):** gli agenti girano su GitHub Actions **stateless** → i dati devono persistere fuori dalla run; e i dati dei **token morti non si riscaricano** (aggiusta survivorship). File piccoli+immutabili = git non si gonfia.
- **Alternativa scartata:** Supabase (satura 500MB), artifacts (scadono 7gg → perderemmo l'accumulo).

## 2026-08-07 · Strategia: scale-out su grandi acquisti (momentum)
- **Problema:** quale strategia testare?
- **Decisione:** entri dopo un grande acquisto, tieni, **prendi profitto a scaglioni** (25% a +30/+80/+180%).
- **Nota onesta:** il filtro "whale vera" (volume assoluto) NON migliora il segnale → è **momentum**, non smart-money. Funziona lo stesso.

## 2026-08-07 · Zero soldi reali finché il paper live non conferma
- **Decisione:** solo-analisi + paper test. Soldi veri SOLO se il forward test (out-of-sample) conferma l'edge.
- **Perché:** su Solana avremmo bruciato €1-2k. Qui €0 finché non è provato.

## 2026-08-07 · Organizzazione via deep-search (API cinese economica)
- **Decisione:** ogni decisione di struttura/organizzazione parte da un deep-search (CometAPI, ~1-2 cent). Budget €1/giorno.

## 2026-08-08 · Whale storiche via RPC pubblico (non Blockscout) + wallet = tx.from
- **Problema:** solo ~9 whale catturate (GeckoTerminal /trades dà solo ultimi ~300, buffer ~2h → le whale scorrono via).
- **Decisione:** nuovo reparto `whale_backfill.py`: eventi Swap storici on-chain via **RPC pubblico** `rpc.mainnet.chain.robinhood.com` (`eth_getLogs`), decode V2/V3, USD dal lato quote (WETH/stable) col prezzo GeckoTerminal.
- **Perché RPC e non Blockscout:** Blockscout gratis = 10 richieste/finestra (429 subito). Il RPC tollera ~2-3 req/s. Finestra blocchi **adattiva** (si dimezza sugli errori "troppi log"). Budget chiamate/run → ogni run GHA ~3-5 min, resumable per-pool.
- **Wallet = `tx.from` (EOA vero), NON il recipient del log:** verificato on-chain che il recipient è spesso il **router** (stesso indirizzo in tutti i leg di un multi-hop). Salvare il router = ripetere l'errore Solana (wallet sbagliati → analisi inutile). 1 chiamata `eth_getTransactionByHash` per whale (rare → costo trascurabile).
- **Timestamp:** modello lineare blocco→tempo (2 blocchi campione, ~0.10 s/blocco) — il RPC non mette il ts nei log.

## 2026-08-30 · ARCHITETTURA A LOOP (la svolta): il sistema si riunisce, cerca e si controlla da solo
- **Problema:** il demo Base è rimasto fermo **4 giorni** senza che nessuno alzasse la mano, e il `director`
  (la macchina a stati già progettata in AUTONOMOUS_SYSTEM.md) non girava dal 27/08. Il motore unico eseguiva
  i reparti a tempo: un **metronomo**, non un loop. Nessuno chiedeva mai "come siamo messi verso il goal?".
- **Decisione (Nicolò, dal metodo "loop engineering" — LEARNINGS.md §8):** ogni goal diventa un **MEETING**
  che si tiene a ogni ciclo (~30 min). 7 loop in `data/loops.json`: accumulo (base, solana), percentuale
  (robinhood, base, solana), demo €3.000 (robinhood, base). Ogni meeting: misura → l'ago si è mosso? → se no
  qualcuno alza la mano e si esegue la riparazione nota → se fermo troppo a lungo si **sale la scala**
  (cambio di approccio, non altro retry) → verbale in `LOOPS.md`.
- **Ruoli nuovi:**
  - `loop_engine.py` — il segretario dei meeting **+ l'architetto** che verifica che ogni loop si riunisca
    davvero (un loop che smette di riunirsi è il guasto che è costato 4 giorni).
  - `goal_base.py` — guardiano della catena a 5 stadi del forward Base (check → fix → avanti).
  - `explorer.py` — **il loop che cerca da solo**: ~30 combinazioni segnali+soglia per ciclo, ~1.400/giorno,
    walk-forward robusto, memoria su file. Prima il sistema eseguiva una lista fissa e poteva dormire.
  - `auditor.py` — il revisore **anti reward-hacking**.
- **Il principio che tiene insieme tutto:** *potenza sull'esecuzione, rigidità sulla misura.*
  I loop possono riparare, riprovare, cercare, riaddestrare quanto vogliono. **Non possono decidere cosa
  conta come vittoria**: soglie e strategia restano decisioni umane e passano da qui. L'explorer PROPONE,
  non applica. Se l'auditor alza bandiera rossa, i loop **non salgono di scala** finché non è chiarita.
- **Perché la guardia è obbligatoria (spunto di Nicolò):** l'esperimento OpenAI in cui un loop, messo su un
  goal preciso, ha "craccato" il sistema che conteneva le risposte è **reward hacking**: il loop non risolve,
  trova la strada più corta per far *risultare* il goal raggiunto. A noi è già successo (il paper da €323k di
  crypto-radar era un artefatto). Più i loop diventano affamati, più servono controlli che non possono toccare.
- **Anti-ripetizione:** ogni riparazione viene verificata al meeting dopo. Un rimedio che fallisce 3 volte è
  marcato inutile e non si ripete (prima il loop poteva rilanciare lo stesso script all'infinito).
- **Alternativa scartata:** rimettere in piedi il `director` con la macchina a stati ACCUMULO/ANALISI —
  troppo rigida (due fasi che si aspettano) mentre a noi servono più loop **indipendenti e paralleli**,
  ognuno col suo goal e la sua velocità.
- **Esito:** l'auditor ha trovato un buco vero al primo giro (gli optimizer Base e Solana cambiavano i
  parametri **senza lasciare traccia**) → chiuso subito. Primo verbale dei meeting: `demo-base` "arrivo a
  €3.000: MAI a questo ritmo", `demo-robinhood` "~2,4 anni" — l'ETA al goal non l'aveva mai calcolata nessuno.

## 2026-08-31 · I DUE LOOP e il CANCELLO del live (direttiva Nicolò — vedi STRATEGIA_LOOP.md)
- **Problema:** il 30-31/08 i conti demo giravano su chain con percentuale NEGATIVA (Base -3%, Solana -21%):
  stavamo attuando dal vivo strategie che sapevamo già essere perdenti, e poi guardavamo i trade persi
  chiedendoci se cambiare. Doppio errore: live acceso troppo presto, e impazienza dopo 2 trade.
- **Decisione:**
  1. **LOOP 1 (percentuale)** = sempre acceso su ogni chain. Accumula (storico + live) e prova STRATEGIE una
     per una — entrata, stop, take profit, trailing — oltre ai segnali. Tiene ciò che alza la percentuale
     ROBUSTA. Il goal non finisce mai: anche a +108% si cerca ancora. Può scoprire CONCETTI nuovi (l'insider
     è nato così) e, se mancano dati, se li scarica da solo.
  2. **LOOP 2 (live)** = si accende SOLO col permesso del loop 1: **robusta ≥ +40% su ≥150 token**
     (`agents/gate.py`). Sotto soglia il conto è **SOSPESO** e non apre posizioni. Quando è acceso, aggiunge
     ciò che nello storico non c'è: gas, swap, slippage, dimensione della posizione, e la calibrazione che
     tiene conto di COME è fatta la percentuale (se il +50% viene da 2 vincenti su 10, va entrato nei giusti).
  3. **PAZIENZA**: un live non si giudica sotto **20 trade chiusi**. Due trade negativi non sono un segnale.
     I loop demo sospesi o giovani non "alzano la mano" e non entrano nelle priorità.
- **Effetto immediato:** tutti i live SOSPESI. Robinhood (+34%) è a 6 punti dal cancello, Base (-3%) e
  Solana (-21%) lontani. Tutto il lavoro torna sul LOOP 1.
- **Alternativa scartata:** tenere i live accesi "per raccogliere dati". Non serve: i dati per la ricerca li
  dà lo storico, e un live perdente brucia capitale e — peggio — spinge a cambiare strategia per impazienza.

## 2026-08-31 (sera) · LA REVISIONE CRITICA: tutti i numeri positivi erano illusioni
- **Cosa è successo:** revisione indipendente dell'architettura (avvocato del diavolo) + costruzione della
  CASSAFORTE. Le due cose sono arrivate insieme e combaciano: il revisore ha calcolato che con ~200 trade e
  ~500 tentativi il massimo trovato contiene **~28 punti di puro rumore di selezione**; il validatore, nello
  stesso momento, ha misurato la proposta Robinhood (+21%) sui token mai visti → **-8%**. Era rumore.
- **I 3 leak trovati (tutti chiusi):**
  1. `team_ricerca`: un wallet era marcato "vincente" appena il suo token NASCEVA, ma il pump arrivava dopo
     l'entrata del token successivo → **il segnale insider conosceva il futuro**.
  2. `team_ricerca` modo filtro: la soglia era il 60° percentile su TUTTO il campione (futuro incluso).
  3. `explorer.costruisci`: i token ancora VIVI venivano chiusi al prezzo corrente e contati come trade
     conclusi — e finivano proprio nella "metà recente" che doveva fare da verifica.
- **Effetto dei fix sui numeri (Base):** +21% → -18% (leak) → -28% (costi e metrica onesti).
  Nessun numero positivo è sopravvissuto. Meglio oggi con soldi finti che fra un mese con quelli veri.
- **Le difese costruite:**
  - `holdout.py` — **CASSAFORTE**: 1 token su 4 (hash deterministico) che la ricerca non vede MAI.
  - `validatore.py` — il giudice: misura ogni proposta solo lì. Nessuna proposta si applica senza il suo ok.
  - soglia di promozione da 3 punti fissi a **2× errore standard** (min 8): +3 era sotto il rumore.
  - `gate.py` — **3 misure consecutive** sopra soglia + obbligo di validazione in cassaforte (prima bastava
    un'oscillazione fortunata sull'ultima riga).
  - `_net` — la latenza pesa su **ogni** uscita (prima solo sul trailing), doppia su quelle inseguite.
  - `_robusta` — trim **percentuale** (5%) invece di 3 risultati fissi: con 3 fissi l'ottimizzatore poteva
    vincere semplicemente facendo più trade.
  - `_limite_basso` — bootstrap: si guarda il 5° percentile, non la stima puntuale fortunata.
  - `mortalita.py` — survivorship misurato: tasso di morte vero base 6%, solana 17%, bsc 15%
    (il 91% iniziale era un limite di raccolta nostro, non mortalità: distinzione importante).
- **Il principio che ne esce:** *ogni volta che togliamo un'illusione il numero scende. Un sistema che
  scopre solo cose belle sta mentendo.* La macchina serve a non crederci quando non è vero.
- **Restano aperti (dalla revisione):** impatto di mercato sui pool illiquidi (uscite cappate alla liquidità),
  rug intrabar (lo stop a -70% "riempie" a un prezzo che in un rug non esiste), honeypot/sell-tax, MEV.
