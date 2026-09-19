# Progettazione Sistema Auto-Alimentante Whale-Radar

## 1. MACCHINA A STATI ESPLICITA

```
                          [BOOT]
                            |
                            v
    +-----------------> ACCUMULO <------------------+
    |                   /       \                   |
    |           IN_CORSO         IN_ATTESA          |
    |              |                 |               |
    |              v                 |               |
    |       (Job running)    (Tutti i job           |
    |              |          completati &          |
    |              |          no nuove directive)   |
    |              +----------------->+             |
    |                                 |             |
    |                                 v             |
    |                         COND_ACCUMULO_FINITO  |
    |                                 |             |
    |                                 v             |
    |                           ANALISI_IN_CORSO    |
    |                                 |             |
    |                                 v             |
    |                         (Analisi completata,  |
    |                          directive generate)  |
    |                                 |             |
    |                                 v             |
    +------------------------ COND_ANALISI_FINITA --+
```

**STATI PRINCIPALI:**
- `BOOT`: Stato iniziale, transizione immediata ad ACCUMULO
- `ACCUMULO`: Raccolta dati attiva
  - Sottostato `IN_CORSO`: Almeno un job di accumulo in esecuzione
  - Sottostato `IN_ATTESA`: Tutti i job completati, in attesa di valutazione
- `ANALISI`: Analisi dati e generazione directive
  - Sottostato `IN_CORSO`: Analyst_core in esecuzione
  - Sottostato `COMPLETATA`: Analisi terminata, directive pronte

**TRANSIZIONI CONDIZIONATE:**
- `BOOT` → `ACCUMULO`: Sempre
- `ACCUMULO_IN_CORSO` → `ACCUMULO_IN_ATTESA`: Quando tutti i job di accumulo schedulati per il ciclo corrente sono `completed/success`
- `ACCUMULO_IN_ATTESA` → `ANALISI_IN_CORSO`: Quando COND_ACCUMULO_FINITO è vera
- `ANALISI_IN_CORSO` → `ACCUMULO_IN_CORSO`: Quando COND_ANALISI_FINITA è vera

## 2. CONDIZIONI DI PASSAGGIO MISURABILI

**COND_ACCUMULO_FINITO (da Fase 1 a Fase 2):**
1. **Nessuna directive pendente**: `directives.json` è vuoto o tutte le directive sono `processed`
2. **Stabilità dei dati**: 
   - `whale_backfill` non ha trovato nuove balene negli ultimi 3 cicli (6-12h)
   - `whale_candles` ha completato scaricamento per tutti i token nella watchlist
3. **Health check passato**: `HEALTH.md` non contiene errori critici (livello > WARNING)

**COND_ANALISI_FINITA (da Fase 2 a Fase 1):**
1. **Report generato**: `analysis_report.md` è stato creato/aggiornato
2. **Directive prodotte**: `directives.json` contiene almeno una nuova directive con stato `pending`
3. **Metriche calcolate**: Sono state aggiornate tutte le metriche in `STATE.md`

## 3. MECCANISMO DI COMUNICAZIONE TRA FASI

### Schema `state.json`
```json
{
  "current_phase": "ACCUMULO",
  "current_subphase": "IN_ATTESA",
  "last_transition": "2024-01-15T10:30:00Z",
  "last_transition_reason": "COND_ACCUMULO_FINITO: Nessuna directive pendente",
  "cycle_id": 42,
  "cycle_start_time": "2024-01-15T08:00:00Z",
  "metrics": {
    "tokens_tracked": 385,
    "tokens_total_universe": 185,
    "whales_identified": 969,
    "wallets_tracked": 352,
    "active_tokens": 62
  },
  "active_directives_count": 0,
  "last_analysis_timestamp": "2024-01-15T09:45:00Z",
  "deep_search_last_run": "2024-01-14T00:00:00Z",
  "deep_search_count_today": 0
}
```

### Schema `directives.json`
```json
{
  "generated_at": "2024-01-15T10:15:00Z",
  "generator": "analyst_core",
  "cycle_id": 42,
  "directives": [
    {
      "id": "dir_42_001",
      "action": "fetch_candles",
      "target": "0x742d35Cc6634C0532925a3b844Bc9e90F90b1A1F",
      "params": {
        "days": 90,
        "interval": "1h"
      },
      "priority": "HIGH",
      "reason": "Token ha attività balena ma solo 7 giorni di candele",
      "created_at": "2024-01-15T10:15:00Z",
      "status": "pending",
      "processed_at": null,
      "processed_by": null,
      "attempts": 0
    },
    {
      "id": "dir_42_002",
      "action": "backfill_wallet",
      "target": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
      "params": {
        "lookback_blocks": 100000
      },
      "priority": "MEDIUM",
      "reason": "Wallet score basato su solo 5 transazioni",
      "created_at": "2024-01-15T10:15:00Z",
      "status": "processing",
      "processed_at": "2024-01-15T10:20:00Z",
      "processed_by": "whale_backfill",
      "attempts": 1
    }
  ]
}
```

**Processo di consumo delle directive:**
1. Agente Fase 1 cerca directive con `status: "pending"`
2. Imposta `status: "processing"`, `processed_by: <agent_name>`, incrementa `attempts`
3. Esegue l'azione
4. Se successo: `status: "processed"`, `processed_at: <timestamp>`
5. Se fallito dopo 3 tentativi: `status: "failed"`, logga errore in `HEALTH.md`

**Rilevamento completamento:** Il `director` controlla se tutte le directive hanno `status: "processed"` o `"failed"`.

## 4. TABELLA DEGLI AGENTI (COMPLETA)

| Nome Agente | Fase | Compito (1 riga) | Input (file letti) | Output (file scritti) | Schedule (Cron GitHub Actions) | Trigger al Termine |
|---|---|---|---|---|---|---|
| `director` | Supervisore | Legge stato, valida condizioni, aggiorna fase, lancia job | `state.json`, `directives.json`, `HEALTH.md` | `state.json`, `STATE.md` (aggiorna) | `*/30 * * * *` | Avvia job della fase target via `workflow_dispatch` |
| `analyst_core` | ANALISI | Analisi statistica, cerca edge, genera gap e report | `*.jsonl.gz`, `state.json`, `token_universe.jsonl` | `analysis_report.md`, `directives.json`, `metrics.json` | Trigger da `director` | Aggiorna `state.json` per tornare ad ACCUMULO |
| `gap_detector` | ANALISI | Sottocomponente di `analyst_core`, rileva gap deterministici | `whale_txs.jsonl.gz`, `candles.jsonl.gz`, `wallet_scores.jsonl.gz` | (interno ad `analyst_core`) | Incluso in `analyst_core` | Passa risultati ad `analyst_core` |
| `deep_search_orchestrator` | ANALISI | Usa API esterna per scoprire gap non ovvi | `analysis_report.md`, `state.json`, `failed_directives.jsonl` | `deep_search_insights.md`, nuove `directives` (tipo "exploratory") | Max 1/giorno, trigger dopo 3 cicli senza edge | Aggiorna `directives.json` con nuove directive exploratory |
| `whale_backfill` | ACCUMULO | Cattura transazioni balene via RPC pubblico | `directives.json` (se presenti), `token_list.json` | `whale_txs.jsonl.gz`, `new_tokens.jsonl` | `0 */4 * * *` (ogni 4h) | Aggiorna `directives.json` (status), notifica a `watchdog` |
| `whale_candles` | ACCUMULO | Scarica candele OHLCV per token | `directives.json` (azione fetch_candles), `token_list.json` | `candles.jsonl.gz`, `candle_coverage.json` | `0 */2 * * *` (ogni 2h) | Aggiorna `directives.json` (status), notifica a `watchdog` |
| `collector` | ACCUMULO | Aggrega dati secondari (pressione acquisto/vendita) | `whale_txs.jsonl.gz`, `candles.jsonl.gz` | `market_pressure.jsonl.gz`, `orderbook_snapshots.jsonl.gz` | `0 */6 * * *` (ogni 6h) | Notifica a `watchdog` |
| `wallet_scores` | ACCUMULO | Calcola performance storica wallet balene | `whale_txs.jsonl.gz`, `candles.jsonl.gz` | `wallet_scores.jsonl.gz`, `wallet_performance.json` | `0 0 */1 * *` (ogni giorno) | Notifica a `watchdog` |
| `watchdog_quality` | Monitor | Monitora qualità, completezza, genera alert | `*.jsonl.gz`, `HEALTH.md`, job logs | `HEALTH.md`, `data_quality_report.md`, email (se errori gravi) | `0 */1 * * *` (ogni ora) | Aggiorna `HEALTH.md`, invia alert se necessario |
| `state_reporter` | Tutte | Genera/aggiorna `STATE.md` per status leggibile | `state.json`, `directives.json`, `analysis_report.md`, `HEALTH.md` | `STATE.md` (sovrascrive) | `*/15 * * * *` (ogni 15 min) | Nessuno (solo aggiornamento file) |

## 5. PSEUDO-CODICE CRITICO

### `director` (logica principale)
```python
def director_main():
    # Leggi stato corrente
    state = read_json("state.json")
    directives = read_json("directives.json")
    health = read_md("HEALTH.md")
    
    # Controlla lock per evitare concorrenza
    if exists(".lock_director"):
        if lock_older_than(30, "minutes"):
            remove(".lock_director")  # Lock stale
        else:
            return  # Esci, già in esecuzione
    
    create_lock(".lock_director")
    
    try:
        if state["current_phase"] == "ACCUMULO":
            if state["current_subphase"] == "IN_CORSO":
                # Controlla se tutti i job accumulo sono completati
                if all_accumulo_jobs_completed():
                    state["current_subphase"] = "IN_ATTESA"
                    write_state(state, "Transizione a IN_ATTESA: tutti job completati")
            
            elif state["current_subphase"] == "IN_ATTESA":
                # Valuta COND_ACCUMULO_FINITO
                if check_accumulo_finito(directives, health):
                    # Transizione ad ANALISI
                    state["current_phase"] = "ANALISI"
                    state["current_subphase"] = "IN_CORSO"
                    state["last_transition"] = now()
                    state["last_transition_reason"] = "COND_ACCUMULO_FINITO soddisfatta"
                    write_state(state)
                    
                    # Triggera analyst_core via workflow_dispatch
                    trigger_github_action("analyst_core.yml")
        
        elif state["current_phase"] == "ANALISI":
            if state["current_subphase"] == "IN_CORSO":
                # Controlla se analyst_core è completato
                if analyst_core_completed():
                    state["current_subphase"] = "COMPLETATA"
                    write_state(state, "Analisi completata")
            
            elif state["current_subphase"] == "COMPLETATA":
                # Transizione di nuovo ad ACCUMULO
                state["current_phase"] = "ACCUMULO"
                state["current_subphase"] = "IN_CORSO"
                state["last_transition"] = now()
                state["last_transition_reason"] = "Directive generate, ritorno ad accumulo"
                state["cycle_id"] += 1
                state["cycle_start_time"] = now()
                write_state(state)
                
                # Triggera job accumulo per processare nuove directive
                trigger_github_action("whale_candles.yml")
                trigger_github_action("whale_backfill.yml")
    
    finally:
        remove_lock(".lock_director")
```

### `gap_detector` deterministico
```python
def detect_gaps_deterministic():
    gaps = []
    
    # 1. Gap di copertura candele
    tokens_with_whale = load_jsonl("whale_txs.jsonl.gz")["token_address"].unique()
    tokens_with_candles = load_jsonl("candles.jsonl.gz")["token_address"].unique()
    
    for token in tokens_with_whale:
        if token not in tokens_with_candles:
            gaps.append({
                "action": "fetch_candles",
                "target": token,
                "params": {"days": 30},
                "reason": f"Token con attività balena ma nessuna candela"
            })
        else:
            # Controlla profondità storica
            candle_days = get_candle_coverage_days(token)
            if candle_days < 30:
                gaps.append({
                    "action": "fetch_candles",
                    "target": token,
                    "params": {"days": 90 - candle_days},
                    "reason": f"Solo {candle_days} giorni di candele, minimo 30 richiesti"
                })
    
    # 2. Gap di dati wallet
    wallets = load_jsonl("whale_txs.jsonl.gz")["from_address"].unique()
    for wallet in wallets:
        tx_count = count_transactions(wallet)
        if tx_count < 10:
            gaps.append({
                "action": "backfill_wallet",
                "target": wallet,
                "params": {"lookback_blocks": 100000},
                "reason": f"Wallet con solo {tx_count} transazioni, campione insufficiente"
            })
    
    # 3. Gap di token nell'universo ma non trackati
    universe_tokens = load_jsonl("token_universe.jsonl")["address"].unique()
    for token in universe_tokens:
        if token not in tokens_with_candles:
            gaps.append({
                "action": "fetch_candles",
                "target": token,
                "params": {"days": 7},
                "priority": "LOW",
                "reason": "Token nell'universo ma non monitorato"
            })
    
    return gaps
```

## 6. LOGICA E TRIGGER PER DEEP-SEARCH

**Trigger Conditions (TUTTE devono essere vere):**
1. **3 cicli consecutivi** senza edge statisticamente significativo (p-value < 0.01 nel report)
2. **Budget disponibile**: < €0.80 spesi oggi (soglia €1/giorno)
3. **Almeno 24 ore** dall'ultima esecuzione
4. **Dati sufficienti**: Almeno 50 token con > 30 giorni di candele

**Frequenza Massima:** 1 volta al giorno

**Processo Deep-Search:**
```python
def deep_search_orchestrator():
    # 1. Prepara contesto per LLM
    context = {
        "analysis_summary": read_file("analysis_report.md"),
        "failed_directives": load_jsonl("failed_directives.jsonl"),
        "current_metrics": read_json("state.json")["metrics"],
        "known_gap_patterns": extract_patterns_from_history()
    }
    
    # 2. Chiama API esterna (es. CometAPI, DeepSeek)
    prompt = f"""
    Analizza questo sistema di trading automatico per memecoin.
    Dati attuali: {context['current_metrics']}
    Problemi recenti: {context['failed_directives']}
    
    Suggerisci 1-3 TIPI DI DATI NUOVI che potrebbero fornire edge statistico.
    Considera: metriche on-chain alternative, correlazioni esterne, pattern temporali.
    Rispondi in JSON: {{"insights": [{{"data_type": "...", "reasoning": "...", "implementation_hint": "..."}}]}}
    """
    
    response = call_external_api(prompt, max_cost=0.02)  # €0.02 per chiamata
    
    # 3. Traduci in directive "exploratory"
    exploratory_directives = []
    for insight in response["insights"]:
        directive = {
            "action": "exploratory_fetch",
            "target": "SYSTEM",
            "params": {
                "data_type": insight["data_type"],
                "exploration_depth": "SHALLOW",
                "max_cost_estimate": 0.10  # €0.10 massimo per questa exploration
            },
            "priority": "LOW",
            "reason": f"Deep-search suggestion: {insight['reasoning'][:100]}...",
            "generator": "deep_search"
        }
        exploratory_directives.append(directive)
    
    # 4. Aggiungi a directives.json (massimo 3 nuove al giorno)
    add_exploratory_directives(exploratory_directives[:3])
```

## 7. SCHEMA `STATE.md`

```markdown
# WHALE-RADAR - Sistema Auto-Alimentante
*Ultimo aggiornamento: 2024-01-15T10:30:00Z (2 minuti fa)*

## 📊 STATO CORRENTE
**Fase:** `ACCUMULO` (IN_CORSO)
**Durata fase corrente:** 4 ore, 30 minuti
**Ciclo #42** (iniziato: 2024-01-15T08:00:00Z)

## 🔄 ULTIMA TRANSAZIONE
**Quando:** 2024-01-15T08:00:00Z
**Da:** ANALISI (COMPLETATA) → ACCUMULO (IN_CORSO)
**Motivo:** 7 nuove directive generate per colmare gap dati

## 🎯 GAP RILEVATI (PRIORITÀ)
1. **ALTA**: 3 token con attività balena ma 0 candele
   - `0x742d...A1F`: Balena acquistata 2 giorni fa, nessuna candela
   - `0x5aA0...7F2`: 5 transazioni balena, candele solo 1 giorno
2. **MEDIA**: 12 wallet con < 10 transazioni storiche
   - Campione insufficiente per calcolo wallet score affidabile

## 📥 ACCUMULO IN CORSO
**Job attivi:** `whale_candles` (in esecuzione da 15 min)
**Directive in elaborazione:** #45 di 52 totali
**Progresso:** 86% (45/52 directive processate)
**Corrente:** Scaricando 90 giorni di candele per `0x742d35Cc6634C0532925a3b844Bc9e90F90b1A1F`

## ⏭️ PROSSIMO STEP ATTESO
**Quando:** ~2024-01-15T10:45:00Z (15 minuti)
**Cosa:** Completamento job `whale_candles`
**Poi:** Valutazione COND_ACCUMULO_FINITO da parte di `director`

## 📈 METRICHE CHIAVE
| Metrica | Valore | Copertura |
|---------|--------|-----------|
| Token totali universo | 185 | 100% (definizione) |
| Token con candele | 385 | 208% (alcuni token multi-chain) |
| Token con attività balena | 62 | 33.5% dell'universo |
| Balene identificate | 969 | +12 nell'ultimo ciclo |
| Wallet tracciati | 352 | +3 nell'ultimo ciclo |
| Giorni dati medi per token | 47.3 | (su 62 token attivi) |

## ⚠️ ALLERT ATTIVI
- Nessun alert critico
- 2 warning: RPC lento per token `0x1f98...a5b` (3 tentativi falliti)

## 🔍 DEEP-SEARCH STATUS
**Ultima esecuzione:** 2024-01-14T00:30:00Z (23.5 ore fa)
**Costo oggi:** €0.15 / €1.00 giornalieri
**Prossima esecuzione possibile:** Dopo le 00:30 UTC (45 minuti)
**Trigger attivo:** SÌ (3 cicli senza edge significativo)
```

## 8. PIANO DI MESSA IN OPERA PASSO-PASSO

### Fase 0: Preparazione (Giorno 0)
1. **Branch di sviluppo**: Creare branch `feat/autonomous-loop` dal main
2. **Documentazione**: Creare `docs/autonomous_system.md` con questo design

### Fase 1: File di Stato e Comunicazione (Giorni 1-2)
1. Creare `schemas/state.schema.json` e `schemas/directives.schema.json`
2. Implementare `scripts/init_state.py` che crea i file iniziali:
   - `state.json` con fase BOOT
   - `directives.json` vuoto
   - `STATE.md` template
3. Committare e push su branch

### Fase 2: Director Base (Giorni 2-3)
1. Creare `.github/workflows/director.yml` con:
   - Cron: `*/30 * * * *`
   - Permessi: `contents: write` per aggiornare file
   - Logica Python base di transizione stati
2. Implementare lock file mechanism (`.lock_