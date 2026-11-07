# 🏎️ WHALE-RADAR — ARCHITETTURA (il master blueprint della "scuderia")

> Sintesi di 6 deep-search (organizzazione, database, docs, skills, multi-agente, metodo). Costo: ~8 cent.
> Questo è **come è fatta la fabbrica**. Ogni reparto, ogni cartella, ogni regola. Si legge in 2 minuti.

---

## 🎯 PRINCIPIO GUIDA
Costruire la **fabbrica prima della produzione**. Ogni pezzo: **un compito, un posto, una regola.**
Tutto **gratis** (GitHub pubblico + Actions + API free). **Anti over-engineering:** il minimo che tiene ordine.

---

## 📁 STRUTTURA CARTELLE (l'albero definitivo)
```
whale-radar/
├── README.md              # portale: cosa/come in 30 sec
├── ARCHITECTURE.md        # QUESTO: il disegno della fabbrica
├── DECISIONS.md           # perché ho scelto X (append, mai cancellare)
├── EXPERIMENTS.md         # cosa ho già testato + risultato (non rifarlo)
├── DATA_DICTIONARY.md     # struttura esatta di ogni file dati
├── TASKS.md               # coda / in corso / fatti
├── CLAUDE.md              # istruzioni per l'agente AI (ordine)
├── .gitignore
├── requirements.txt
├── agents/                # I REPARTI (ogni agente = 1 file, 1 compito)
│   ├── accumulator.py     # (era tracker.py) fotografa la chain + paper test
│   ├── wallet_sniffer.py  # trova le whale vere (Blockscout)
│   ├── chart_scanner.py   # pattern del grafico attorno all'evento
│   ├── backtest_runner.py # walk-forward sui segnali
│   ├── watchdog.py        # controlla che tutti girino, avvisa se no
│   └── reporter.py        # report giornaliero in markdown
├── lib/                   # codice condiviso (no duplicati)
│   ├── apis.py            # GeckoTerminal / Blockscout / DexScreener
│   ├── storage.py         # scrittura/lettura file compressi
│   └── deep_search.py     # chiamate all'AI cinese (con tetto costo)
├── analysis/              # strumenti on-demand (non girano da soli)
│   ├── analyze.py · walkforward.py · collect_events.py
├── data/                  # I DATI (committati compressi — vedi regola persistenza)
│   ├── raw/               # IMMUTABILE, solo append (sacro)
│   │   └── snapshots/AAAA-MM/GG/HHMM.jsonl.gz
│   ├── processed/         # derivato, RICREABILE (events, candles)
│   │   └── events.jsonl.gz
│   ├── results/           # output analisi (paper_state, stats, backtest)
│   └── state/             # stato corrente (paper_state.json)
├── reports/               # report giornalieri (report_AAAA-MM-GG.md)
├── prompts/ · results/    # i deep-search (prompt + risposte AI)
└── .github/workflows/     # un workflow per agente
```

---

## 🤖 I REPARTI (agenti) — tabella con orari e costo
| Agente | Compito (1 frase) | Ogni quanto | Ora UTC | Scrive in | Costo |
|---|---|---|---|---|---|
| **ACCUMULATOR** | fotografa la chain + paper test | 1h | :00 | `raw/snapshots/` + `state/` | €0 |
| **WATCHDOG** | controlla che tutti girino, avvisa | 1h | :30 | `results/health.json` (+ Issue) | €0 |
| **WALLET_SNIFFER** | trova le whale VERE (chi compra forte) | 6h | 02/08/14/20 | `processed/wallets.jsonl.gz` | ~€0,10/gg (AI) |
| **CHART_SCANNER** | pattern grafico attorno all'evento | 6h | 00/06/12/18 | `processed/events.jsonl.gz` | €0 |
| **BACKTEST_RUNNER** | walk-forward sui segnali | 1/gg | 04:00 | `results/backtest_*.json` | €0 |
| **REPORTER** | report giornaliero markdown | 1/gg | 08:00 | `reports/` | ~€0,05/gg (AI) |
**Totale AI: ~€0,15/giorno** (dentro il budget €1). Regola: **1 solo agente scrive in ogni cartella.**

---

## 🗄️ ARCHITETTURA DATI (gratis, poco spazio, scala)
- **RAW** = grezzo immutabile, solo append, **compresso .jsonl.gz**, partizionato per data. **Keep forever.**
- **PROCESSED** = derivato, ricreabile dal raw (events, candles). Keep 6 mesi.
- **RESULTS/STATE** = output + stato. Keep 1 anno.
- **Query:** DuckDB legge i file compressi direttamente (milioni di righe in <1s, gratis). No database ora.
- **⚠️ REGOLA PERSISTENZA (nostra deviazione motivata):** i dati NOSTRI vengono committati compressi nel
  repo (non gitignorati), perché: (a) gli agenti girano su GitHub Actions **stateless** → i dati devono
  persistere fuori dalla run; (b) i dati **non sono riproducibili** (un token morto non lo riscarichi).
  I file raw sono **piccoli e immutabili** → git non si gonfia. Se un giorno pesano troppo → GitHub Releases (2GB) o Backblaze B2 (10GB free).

---

## 📋 DOCUMENTAZIONE (6 file, ognuno un ruolo, niente doppioni)
| File | Cosa contiene | Aggiorno quando |
|---|---|---|
| `README.md` | cosa/come, mappa | cambia il setup |
| `ARCHITECTURE.md` | il disegno (questo) | cambia la struttura |
| `DECISIONS.md` | perché ho scelto X (Problema→Decisione→Alternativa→Esito) | prendo una decisione |
| `EXPERIMENTS.md` | tabella: data, obiettivo, metodo, risultato, conclusione | finisco un'analisi |
| `DATA_DICTIONARY.md` | schema esatto di ogni file dati | cambia un formato |
| `TASKS.md` | coda / in corso / fatti | inizio/finisco un task |

---

## ✅ REGOLE FERREE (anti-caos, dal fallimento Solana)
1. **1 script = 1 compito.** Niente script sparsi: solo in `agents/`, `lib/`, `analysis/`.
2. **1 solo scrittore per cartella dati.** RAW è sacro (immutabile). PROCESSED è ricreabile.
3. **Dati sempre compressi + immutabili** (niente file giganti riscritti → niente gonfiore git).
4. **Dataset versionati** (`events_v2`), mai sovrascrivere in silenzio.
5. **Ogni decisione va in DECISIONS.md** (se ci pensi >30 min, scrivila).
6. **Ogni esperimento va in EXPERIMENTS.md** (per non rifarlo).
7. **Zero soldi reali** finché il paper live non conferma l'edge.
8. **Costo AI con tetto** (€1/giorno). Ogni chiamata loggata in `costs_log.txt`.

---

## 🗺️ ROADMAP DI COSTRUZIONE (fase per fase, come una scuderia)
- **Settimana 1 — le fondamenta:** ACCUMULATOR (già c'è) → WATCHDOG → riorganizzo il repo in questa struttura.
- **Settimana 2 — i sensori:** WALLET_SNIFFER (chi compra) + CHART_SCANNER (il grafico).
- **Settimana 3 — il cervello:** BACKTEST_RUNNER (walk-forward automatico) + REPORTER (report giornaliero).
- **Poi — la decisione:** se il paper live conferma → soldi veri piccoli. Se no → stop, €0 perso.

**La fabbrica si costruisce un reparto alla volta. Ognuno gira da solo prima di aggiungere il successivo.**
