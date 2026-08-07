# 🐋 WHALE-RADAR — PIANO MADRE (draft v0.1 — si raffina INSIEME nei prossimi giorni)

> **Regola #0 di questo progetto:** NON si scrive codice di produzione finché l'organizzazione non è
> completa e condivisa. Prima si progetta fino al millimetro, poi si costruisce. L'errore da evitare
> (già vissuto): 2 mesi di lavoro per scoprire di aver seguito bot da $6. Mai più.

---

## 🎯 NORTH STAR
Trovare un edge REALE seguendo le **whale vere** (capitale grande, posizioni decise) su chain con
capitale reale (partiamo da **Robinhood chain**), e — SOLO dopo averlo provato coi dati — tradarlo con
disciplina. Obiettivo economico modesto e realistico: su €3.000 basta **~16%** per fare €500.

## ❓ LA DOMANDA CHE L'AZIENDA DEVE RISPONDERE PER PRIMA (prima di tradare 1€)
> *"Quando una whale VERA (capitale ≥ X, posizione ≥ Y) entra in un token, cosa succede DOPO — in media,
> su TUTTE le entrate (vincenti E perdenti), non solo su quelle che vedo già pompate?"*

Se la risposta è "sale con edge positivo e persistente" → **abbiamo trovato oro, costruiamo l'esecutore.**
Se è "in media no" → lo sappiamo coi dati, gratis, senza aver rischiato un euro. **Il forward test è il giudice.**

## 🧭 IL PRINCIPIO ANTI-ILLUSIONE (scritto qui perché non lo dimentichiamo)
I grafici mostrano solo i **vincitori** (survivorship bias — è ciò che ci fregò col paper da €323k). Un
token che vediamo a $53M lo vediamo *perché* ha vinto. La verità sta nel misurare **TUTTE** le entrate
whale in avanti nel tempo, non nel guardare all'indietro i grafici belli.

---

## 👥 I 4 REPARTI (ognuno fa UNA cosa, con compiti GIGANTI e chiari)

### 1) 📥 ACCUMULATORE — "raccoglie i dati grezzi, non giudica" — [DETTAGLIATO, template]
**Scopo:** costruire il dataset grezzo di TUTTE le entrate whale + il comportamento dei token attorno.

**Fonte dati:** Blockscout Robinhood (`robinhoodchain.blockscout.com/api/v2`) — **GRATIS, pubblico**. Verificato
funzionante (stats, holders, token-balances, transfers). Rispettare rate-limit.

**Sotto-compiti (pipeline a stadi):**
- **A. Scoperta TOKEN candidati.** Ogni ciclo: prendi i token attivi della chain. Filtra: market cap in una
  fascia [TBD, es. $500k–$100M], volume_24h ≥ [TBD], reputation non-scam, LP presente. → lista token "vivi".
- **B. Scoperta WHALE.** Per ogni token vivo: top holder + grandi compratori recenti (da token-transfers).
  Classifica **whale candidata** se: valore portafoglio ≥ [TBD, es. $50k], posizione nel token ≥ [TBD, es.
  $10k], è un **WALLET** (non contratto/LP/CEX/bridge — filtro is_contract + lista tag noti).
- **C. Log ENTRATE.** Per ogni whale, registra OGNI acquisto: `wallet, token, ts, prezzo_entrata, size_usd,
  mcap_al_momento, volume_al_momento, età_token`. Idempotente (unico su wallet+token+tx_hash).
- **D. SNAPSHOT chart.** Per ogni token toccato da una whale, cattura la serie prezzo/volume/mcap nel tempo
  (OHLCV) → serve all'Analista per (a) esiti forward, (b) **analisi del grafico** (vedi sotto).

**Output:** tabelle `wallets`, `entrate_whale`, `token_snapshot`. **NON calcola profitti, NON decide.**

**Cadenza:** ogni [TBD] ore. **Test di validazione dell'Accumulatore (da fare PRIMA di fidarci):** su 10
token noti, verificare a mano che le whale trovate siano vere e le entrate corrette. Se sbaglia → si aggiusta.

### 2) 🔬 ANALISTA — "trasforma i dati in statistica onesta" — [DA DETTAGLIARE INSIEME]
**Scopo:** rispondere alla Domanda. Per ogni entrata whale calcola l'**esito forward** (+1h/+6h/+1g/+3g/+7g:
ritorno, max, min, drawdown) e aggrega in statistiche per classe di whale / mcap / volume / pattern-grafico.
**+ ANALISI DEL GRAFICO** (richiesta di Nicolò): come si comporta il chart quando entra una whale — era piatto
prima? spike di volume? accumulo lento vs pump? Queste diventano **feature** che spiegano quando l'entrata funziona.
Include il test di **persistenza** (regge in 2 metà temporali?) e lo split vincenti/perdenti.
> Da definire insieme: le classi, gli orizzonti, le feature-grafico esatte, le soglie di "edge provato".

### 3) 🛡️ AUDITOR — "il senior che si auto-controlla" — [DA DETTAGLIARE INSIEME]
**Scopo:** ciò che mancava e ci è costato 2 mesi. Ogni [settimana] verifica coi dati le ASSUNZIONI base:
- Le whale che seguiamo sono ancora VERE (capitale reale, non bot/contratti)?
- Il segnale regge o è degradato?
- Il codice fa quello che dice la strategia (compliance)?
Se qualcosa non torna → **ALLARME**, si ferma tutto. Registro in `AUDIT_ASSUNZIONI.md`.

### 4) ⚙️ ESECUTORE — "trada" — **SPENTO fino a edge provato** — [DA DETTAGLIARE DOPO]
Si accende SOLO se l'Analista dimostra edge positivo+persistente. Strategia proposta da Nicolò: entri quando
entra la whale vera, **tieni**, prendi profitto **a scaglioni** salendo (non temi i dip, perché le whale vere
non escono in fretta). Da progettare al millimetro solo a valle del sì.

---

## 🗄️ DATABASE (Supabase — riusiamo bene, schema PULITO e nuovo)
`wallets` (address, chain, capitale_usd, prima_vista, classe, is_contract) ·
`entrate_whale` (id, wallet, token, chain, ts, prezzo, size_usd, mcap, volume, età) ·
`token_snapshot` (token, chain, ts, prezzo, mcap, volume, liquidità) ·
`esiti` (entrata_id, ret_1h, ret_6h, ret_1g, ret_3g, ret_7g, max_ret, min_ret, drawdown) ·
`chart_feature` (entrata_id, piatto_prima?, spike_volume?, pattern, ...)

## 🏗️ INFRA (decisione da confermare)
- **GitHub: NUOVO repo pulito** `whale-radar` (il vecchio crypto-radar è gonfio e legato al Solana morto →
  lo lasciamo IN PAUSA, già spento). Repo nuovo = partenza pulita, storia chiara. **Budget-cap GitHub Actions
  dal giorno 1** (lezione dei €127).
- **Supabase:** schema/progetto nuovo e pulito per questi dati.
- **Dati:** Blockscout Robinhood (gratis). Se servono più chain → si valuta fonte per ognuna (sempre gratis prima).
- **Costo totale previsto: ~€0** (Blockscout free + Actions leggero con cap + Supabase free).

## ✅ DISCIPLINA (le regole ferree, dal fallimento precedente)
1. **Solo analisi finché l'edge non è provato.** Zero trading, zero wallet caldo, zero rischio.
2. **Forward test = giudice.** Mai fidarsi dei grafici all'indietro.
3. **Auditor settimanale** verifica le assunzioni base. Mai più errori scoperti dopo 2 mesi.
4. **Accumula → analizza → decidi coi numeri.** Pazienza: anche 1 mese di solo accumulo va bene.

---

## ❓ DA DECIDERE INSIEME (le prossime "giornate di organizzazione")
1. Le **soglie**: cosa rende un wallet "whale" (capitale min? size min?)? Quali token (fascia mcap/volume)?
2. Le **feature-grafico** esatte da estrarre (cosa guardiamo del chart quando entra una whale?).
3. Gli **orizzonti** e la definizione di "edge provato" (numeri precisi).
4. **Multi-chain** subito o solo Robinhood per iniziare?
5. Nome/struttura repo + schema Supabase definitivo.
6. Cadenze esatte di Accumulatore / Analista / Auditor.

> Questo è il draft v0.1. Nei prossimi giorni riempiamo ogni reparto "fino al millimetro", uno alla volta.
