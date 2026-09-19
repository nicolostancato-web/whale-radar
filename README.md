# 🐋 WHALE-RADAR — mappa del progetto (come siamo organizzati)

> **GOAL:** capire se, seguendo i grandi acquisti sulla chain Robinhood (entri, tieni, take-profit a
> scaglioni), c'è un edge REALE — e provarlo **coi dati, senza rischiare un euro**, prima di andare live.
> Target economico: +16% su €3k = €500. **Costo del progetto: €0** (tutto free tier + repo pubblico).

---

## 📊 DOVE SIAMO OGGI
- ✅ Chain + whale reali **verificate** on-chain (wallet $360k, token $53M).
- ✅ Backtest (607 eventi, net fee+slippage): strategia scale-out **+8-13%**, **regge walk-forward** (+13,2%
  out-of-sample) e **robusta sui parametri** (3x-8x tutti positivi). **NON overfit.**
- 🔴 **Buco unico rimasto: survivorship** (i dati storici hanno solo i token vivi). → lo chiude il paper live.
- 🟢 Paper test live + accumulo dati: **in corso**.

---

## ⚙️ COSA GIRA DA SOLO (automatico · ogni ora · gratis · PC spento)
**`tracker.py`** via GitHub Actions (`.github/workflows/paper.yml`, cron orario) fa 2 cose insieme:
1. **Paper test live** — cattura i grandi acquisti in avanti (out-of-sample), simula la strategia,
   traccia il P&L → `data/paper_state.json`.
2. **Accumulatore archivio** — fotografa TUTTA la chain ogni ora in file **compressi immutabili**
   `data/snapshots/GG/HHMM.jsonl.gz` (poco spazio, niente gonfiore git). Registra i token **mentre
   sono vivi** → col tempo **aggiusta il survivorship**.

---

## 🔬 GLI STRUMENTI (li lancio io quando serve, non girano da soli)
| Script | Cosa fa |
|---|---|
| `collect_events.py` | **FASE 1**: su TUTTI i pool, per ogni grande-acquisto salva grafico-PRIMA + esito-DOPO → `data/events.jsonl.gz` |
| `analyze.py` | i 5 test (campione, slippage, filtro whale, simulazione strategia) |
| `walkforward.py` | test out-of-sample dentro la storia + robustezza parametri |
| `collect.py` | scarica pool+OHLCV grezzi → `data/dataset.json` |

---

## 🗄️ I DATI (dove stanno · compressi · poco spazio)
| File | Cos'è | Cresce |
|---|---|---|
| `data/paper_state.json` | posizioni paper aperte/chiuse + P&L | lento |
| `data/snapshots/…jsonl.gz` | archivio orario di tutta la chain (compresso) | +1 file/ora, piccolo |
| `data/events.jsonl.gz` | dataset eventi: grafico-prima + esito-dopo | a ondate (quando lancio la raccolta) |

**Regola spazio:** dati grezzi = MAI in file giganti riscritti (gonfia git). Sempre **compresso + immutabile**.

---

## 🗺️ LE FASI (roadmap chiara)
- **FASE 1 — dati grafico+esito** *(in corso)*: migliaia di eventi → capire QUALI setup funzionano, COME entrare.
- **FASE 2 — dimensione WALLET**: aggiungere "chi entra" (parsing swap Blockscout) → QUALI whale seguire.
- **FASE 3 — decisione**: se il paper live conferma il +8-13% forward → **soldi veri PICCOLI**. Se no → stop, €0 perso.

---

## ✅ LE REGOLE FERREE (per non ripetere Solana)
1. **Zero soldi reali** finché il paper live non conferma l'edge in avanti.
2. **Il forward test è il giudice** — mai fidarsi dei grafici col senno di poi (survivorship).
3. **Ogni numero netto di costi** (fee 2% + slippage). La mediana (caso tipico) conta più della media.
4. **Tutto €0, tutto tracciato, tutto compresso.** Nessuna fattura a sorpresa.
