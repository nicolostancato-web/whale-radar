# RECOVERY — whale-radar  ·  HANDOFF (Claude: LEGGI TUTTO QUESTO PRIMA DI AGIRE)

> **Se stai leggendo questo in una chat NUOVA:** questo file + la tua memoria (si carica da sola) +
> `whale-radar/CLAUDE.md` ti danno TUTTO. Sei la continuazione ESATTA della sessione precedente con Nicolò.
> Leggi tutto, conferma a Nicolò che hai recuperato lo stato, poi riprendi dal **PROSSIMO STEP**.

## 🎯 COSA STIAMO FACENDO (1 frase)
Costruire un tool profittevole di trading memecoin: trovare l'edge sui dati (multi-chain) senza rischiare soldi
veri, poi scalarlo. Fase attuale: accumulo dati giorno-0 + validazione edge in forward (conti demo-live).

## 🔥 MINDSET (INVIOLABILE — dettagli in whale-radar/CLAUDE.md regola #0)
Il tool SI FA, è una CERTEZZA da costruire. L'ipotesi "perdere / non pagherà / l'edge non esiste" NON ESISTE,
non è nel vocabolario. Si va in LOOP finché la percentuale sale. MAI proporre altri progetti, MAI deviare, MAI
dubitare dell'esito. Solo Nicolò decide quando fermarsi. Dall'agente esce solo "come lo miglioriamo".

## 📊 STATO ATTUALE (30/08/2026) — sistema 🟢 verde
**Il MOTORE UNICO** (`agents/engine.py` + `.github/workflows/engine.yml`) gira in loop 5.5h, esegue TUTTI i reparti
in sequenza ogni ~30min, committa ogni ciclo, si auto-riavvia (secret WR_PAT). È nato perché i cron di GitHub sono
inaffidabili su repo affollati (saltavano → reparti fermi 9-15h). Ora solo ~7 workflow attivi. `workflow_watchdog`
sorveglia e ri-lancia i fermi ogni 2h. Tutto €0 (repo pubblico + API free).

**Edge per chain** (dal cervello `multichain_brain`, walk-forward onesto):
- 🟢 **Robinhood** = PROVEN. Media **+60%**, **robusto +34%**, vinti 36%, 230 token. Modello di selezione AUC 0.777.
  Demo-live forward **€122 (+22%)** in 6.5 giorni, 2 trade chiusi. Dati completi. L'ago sale da 10 giorni (+25%→+60%).
- 🟢 **Base** = FORTE. Media +106% generica / +128% con strategia dedicata (entry +2h, TP 4x/15x), robusto +45%.
  Demo-live €100 fermo a **0 trade** → **causa trovata e FIXATA il 30/08** (vedi sotto). Parametri `data/strategy_base.json`.
- 🟡 **Solana** = ANGOLO INSIDER APERTO (30/08). Le feature classiche danno -16%, ma il nuovo `wallet_insider`
  mostra **lift +19.6 punti** di win-rate (27% vs 8% base) e media strategia **+5% vs -32%**, p=0.005 su 22 token.
  Positivo in TUTTE e 18 le configurazioni provate (finestra 30/60/120min × soglie) → non è un parametro fortunato.
  Serve arrivare a 40 casi prima di dichiararlo. `data/strategy_solana.json`, report `INSIDER.md`.
- 🔴 **BSC** = no edge. Coverage 15%.

**Demo-live**: forward puro (entra solo su token nati DOPO l'apertura). Robinhood attivo (+22%), Base in sblocco.

## 🔧 30/08 — perché Base era a 0 trade: DUE colli, entrambi risolti
**(a) Il collector era cieco sui freschi.** Sceglieva i pool da scaricare in ordine di scoperta (FIFO): su Base
nascono ~1400 pool/giorno e ne scaricavamo ~300, quindi la coda dei "mai scaricati" cresceva più in fretta di
quanto la smaltivamo e i token freschi non venivano raggiunti MAI. Verificato: **3914 pool Base nati dopo
l'apertura del demo = 0 file candele**. Il demo non li scartava, non li VEDEVA. Fix: priorità ai giovani (3-96h,
quota 70%), checkpoint ogni 20 candele, `BUDGET_SEC=110` (l'engine killa a 130s e il lavoro si perdeva).

**(b) Il vero collo era il rate limit.** Anche col fix, solo ~8 candele per run. Misurato: le chiamate OHLCV
GeckoTerminal tornano **0.5s oppure 24.8s**, e le lunghe sono i 3 retry interni dopo un **429**. Il free tier ci
rifiuta il **60% delle chiamate anche a 1 ogni 6 secondi** — non è il ritmo, è saturo. Con budget 110s bastavano
4 rate-limit per finire il run senza scaricare niente.
→ **Soluzione: `agents/pulse.py`** (nuovo reparto). DexScreener risponde a **30 pool in UNA chiamata in 0.2s**
(gratis, no chiave). Non dà lo storico OHLCV, ma non serve: il motore gira ogni 30 min, quindi **le candele dei
token giovani ce le costruiamo IN AVANTI** campionandoli, e ogni punto porta già buys/sells (il FLOW) senza
scaricare i trade. Primo run reale: **418 token Base freschi e vivi** (liq>$5k) in 46s, contro gli 8 di prima.
Scrive `data/multichain/<chain>/pulse/<addr>.jsonl.gz`, stesso formato dei candele. `multichain_brain.serie_files()`
le unisce (candele + pulse) e `demo_live_base` le usa. **Servono ~2.5h di motore (5 punti) prima che un token
diventi analizzabile.**

**(c) Il GC domenicale ci lavorava contro.** `data_prune` cancellava ogni token con <5 candele *e lo toglieva da
pools.json* — ma un token nato 3h fa ha 3-4 candele PERCHÉ È NATO DA POCO. Il GC del 30/08 (09:45) ha rimosso
~4400 file. Danno reale limitato (il fix collector era attivo da 1h, i freschi non erano ancora scesi: il file
candele Base più giovane aveva 163h), ma la settimana prossima avrebbe raso al suolo l'accumulo fresco.
Fix: grazia di 48h ai giovani + mai cancellare su errore di lettura. **Nota: `repo_gc` fa `git push -f` su branch
orphan → la storia viene squashata, i dati cancellati NON si recuperano dal git log.**

## 🔁 ARCHITETTURA A LOOP (svolta del 30/08 sera — leggi DECISIONS.md per il dettaglio)
Il sistema non è più un metronomo che riesegue una lista: ora **si riunisce, cerca e si controlla da solo**.
A ogni ciclo del motore (~30 min) girano, in quest'ordine:
1. **`pulse.py`** — dati freschi dei token giovani (DexScreener, 30 pool/chiamata).
2. **`explorer.py`** — ~30 combinazioni nuove segnali+soglia per ciclo (~1.400/giorno), walk-forward robusto,
   memoria su file, una chain a rotazione. **Propone, non applica.** Verbale: `EXPLORER_<chain>.md`.
3. **`auditor.py`** — il revisore anti reward-hacking. Se alza bandiera rossa i loop **non salgono di scala**.
   Verbale: `AUDIT.md`.
4. **`goal_base.py`** — la catena a 5 stadi del forward Base (check → fix → avanti). `GOAL_BASE.md`.
5. **`loop_engine.py`** — i **7 MEETING** (uno per goal) + **l'architetto** che verifica che ogni loop si
   riunisca davvero. Registro in `data/loops.json`, verbale in **`LOOPS.md`** (con le 3 priorità del momento).

**Il principio:** potenza sull'esecuzione, rigidità sulla misura. I loop riparano/cercano/riprovano quanto
vogliono; **non possono decidere cosa conta come vittoria** (soglie e strategia = DECISIONS.md).

## ✅ STATO AL MATTINO DEL 01/09 — la notte del loop autonomo

**I TRE LOOP (nomenclatura ufficiale, vedi STRATEGIA_LOOP.md):**
- **LOOP 0 · ISPEZIONE** — processo permanente (`ispezione_loop.py` + workflow `loop0`), ispeziona ogni 15
  min. Non dipende piu' dai cron di GitHub (saltati 3 volte in un giorno). Verdetto per chain.
- **LOOP 1 · PERCENTUALE** — uno per chain, gira in continuo (`ricerca` + motore).
- **LOOP 2 · DEMO LIVE** — tutti fermi dal cancello: nessuna chain ha una percentuale robusta positiva.

**LA NOTTE (loop autonomo di Claude Code, controllo ogni 45 min):** trovati e chiusi 5 guasti che nessuno
vedeva, e completate le 3 correzioni della revisione critica.

### I guasti trovati e chiusi
1. `explorer_rh` **crashava da 7 ore** (`unpack di 8 valori in 6`) senza dire niente → corretto, e ora
   scrive un verbale anche quando fallisce. *Un agente che tace non si distingue da uno che non esiste.*
2. **Memoria che paralizzava**: 209 segnali su 209 archiviati, i ricercatori puntuali e fermi ("0 provati").
   Ora un caso si riapre anche dopo 12h, non solo se i dati raddoppiano — e se tutto e' bloccato si
   riprendono comunque le idee provate meno di recente. **Nessun componente sta mai a mani vuote.**
3. **Il verdetto del Giudice non chiudeva la proposta**: bocciata a -49% in cassaforte, restava sul tavolo
   col suo +67%. Ora esce dalla coda e va nel cimitero → il GIRO COMPLETO finalmente si chiude.
4. Falso allarme sull'accumulo (confronto tra ispezioni a 15 min contro collector a 30) → finestra oraria.
5. Falso allarme sul Giudice ("non lavora" proprio dopo aver bocciato tutto) → **"niente da fare" non e'
   "non ha lavorato"**.

### Le 3 correzioni della revisione critica — TUTTE CHIUSE
- **Latenza su OGNI uscita** (prima solo sul trailing).
- **Rug intrabar**: lo stop guarda il MINIMO della candela. Dentro l'ora un memecoin crolla a -95% e
  risale: uscivamo a -70%, un prezzo che in un crollo non esiste. Applicato a tutte e 4 le chain —
  Robinhood era rimasta indietro ed era **proprio la chain candidata al live**.
- **Impatto di mercato**: sui pool sottili sei tu il mercato. Il 43% dei token Base costa oltre +10% extra
  in uscita, un quarto arriva al tetto del 45%.

### LA LAVAGNA CON I COSTI ONESTI (01/09, 01:38)
| chain | robusta |
|---|---|
| base | **-29%** |
| bsc | -46% |
| solana | -49% |
| robinhood | **-54%** (era +34% col metro vecchio) |

**Tutte negative.** Non e' un peggioramento del sistema: e' la fine di un'illusione. Ogni volta che abbiamo
tolto un'ottimismo il numero e' sceso — e un sistema che scopre solo cose belle sta mentendo.
Il Giudice ha bocciato **tutte** le proposte passate dalla cassaforte (5 su 5, poi altre 2).

### Resta aperto (limite noto, non lavoro fattibile subito)
**Honeypot e sell-tax**: il prezzo che vediamo non e' sempre un prezzo a cui si puo' VENDERE. Servono dati
che oggi non abbiamo.

## ▶️ PROSSIMO STEP (mattina del 01/09)
1. **Guardare il consumo di quota della notte** (era la prima cosa che Nicolò voleva controllare).
2. Decidere insieme: con tutte le chain negative col metro onesto, dove si cerca? Le opzioni sul tavolo:
   segnali nuovi (l'unica cosa che ha prodotto promozioni), oppure una finestra d'entrata diversa, oppure
   accettare che su queste 4 chain con questi costi non ci sia edge e cambiare terreno.
3. Il LOOP 0 e' stabile: si puo' tornare a guardare la lavagna.

## 🛠️ COME LAVORARE (importante)
- Il repo LOCALE (`~/n8n builder/whale-radar`) è VECCHIO/desincronizzato → **lavorare sul REMOTO**: leggere via
  `raw.githubusercontent.com`, pushare via **GitHub Contents API** (no `git clone`, il repo ha 112MB di bloat).
- NON ri-abilitare i ~16 workflow disabilitati: girano DENTRO il motore (doppione se riattivati).
- Report **"news?"** = usa il formato tabella standard (memoria `feedback_news_report_format`): per chain →
  accumulo % / max reale / ETA / **% forward (edge, media + robusto)** / demo-live.
- Backup chat in `~/Documents/whale-radar-backups/`. Aggiorna QUESTO file a ogni milestone e committa+pusha.

## 🔑 RISORSE / CREDENZIALI
- Repo: `github.com/nicolostancato-web/whale-radar` (PUBBLICO → mai committare segreti)
- GH_TOKEN: nel CLAUDE.md della working dir principale (`~/n8n builder/CLAUDE.md`, riga GitHub)
- Helius (Solana giorno-0): 2 key in `~/Documents/b2b-finder-credentials.txt` (secret GitHub: HELIUS_API, HELIUS_API2)
- WR_PAT: secret GitHub (auto-dispatch del motore)
- RPC pubblici gratis: `mainnet.base.org` (Base), `bsc.rpc.blxrbdn.com` (BSC archive)

## 🧩 ARCHITETTURA — i 3 loop, TUTTI sempre attivi in parallelo
1. **Accumulo** (collector: candele, trade giorno-0, pool) → cresce sempre.
2. **Percentuale/Learning** (`multichain_brain` + `learner` + `strategy_optimizer_<chain>`) → ri-analizza TUTTO
   l'accumulo di continuo, ri-addestra il modello di selezione, ottimizza la strategia. NON aspetta che l'accumulo
   finisca. Più dati → impara meglio → % sale e diventa più robusta.
3. **Demo-live** (`demo_live`, `demo_live_base`) → prova forward con soldi finti + costi/latenza reali.
Ogni chain valida ha il suo optimizer dedicato: `strategy_optimizer` (Robinhood), `_base`, `_solana`.

## 📜 STORICO MILESTONE (sintesi, dal più recente)
- 30/08 pom: trovato il collo VERO (rate limit OHLCV GeckoTerminal, 60% di 429) → creato **`pulse.py`**:
  candele costruite in avanti via DexScreener, 30 pool/chiamata, 418 token Base freschi al primo colpo.
  Fixato il GC che cancellava i token giovani. Motore riavviato per caricare il codice nuovo.
- 30/08: **fix collector FIFO→giovani** (Base era cieco sui token freschi: 3914 pool senza candele → demo a 0 trade).
  Creato **`wallet_insider.py`**: primo segnale POSITIVO su Solana (lift +19.6pt, p=0.005, media +5% vs -32%),
  robusto su 18 configurazioni. Orizzonte di risoluzione portato a 24h (a 168h lo storico wallet non si popolava mai).
- 29/08: creato loop Solana (strategy_optimizer_solana, nel motore); verdetto "serve feature insider". Formato news
  standard salvato. Fix candele Base prioritarie. Regola mindset #0 scritta (dopo un mio errore: avevo dubitato).
- 27-28/08: MOTORE UNICO creato (fine throttling: GitHub saltava i cron). 21→~7 workflow. Auto-riavvio WR_PAT.
- 26/08: watchdog reparti (self-heal). Fix RPC/frequenze. demo_live_base creato (strategia Base dedicata TP 15x).
- 25/08: collector day-0 EVM (BSC bloXroute, Base mainnet.base.org, binary search blocco listing).
- notte 25→26: Solana v2 (salto diretto al giorno-0 via Helius), coverage 28%→66%.
- Base: DEX = Uniswap V3 (catturato) + Aerodrome/morti (tetto ~45-50%). BSC: address pool ≠ contratto per molti (tetto basso).

## COME RIPRENDERE
"Apri chat nuova → 'leggi RECOVERY_whale-radar.md, costruiamo le feature insider per Solana' → il nuovo Claude
recupera tutto e riparte dal PROSSIMO STEP." Il sistema intanto gira da solo (motore + watchdog). Niente si perde.
