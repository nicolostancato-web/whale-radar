#!/usr/bin/env python3
"""
DIRECTOR — il regista del loop auto-alimentante (macchina a stati FASE1<->FASE2).
Gira ogni ora. Se e' ora di analizzare (intervallo o mai fatto), lancia analyst_core (FASE 2),
legge i gap trovati, li registra come "cosa accumulare" per la FASE 1, aggiorna state.json e scrive
STATE.md (il pannello 'news?'). L'accumulo (Fase 1) gira sempre coi suoi cron; il director alterna
il FOCUS del sistema e chiude il loop. Nessuna chiamata esterna. €0.
"""
import json, os, time, glob, gzip, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # per importare analyst_core dalla stessa cartella
import analyst_core

STATE = "state.json"
ANALYSIS_EVERY_H = 6      # rifai l'analisi ogni 6h (l'accumulo intanto va avanti)
now = int(time.time())


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"current_phase": "ACCUMULO", "cycle_id": 0, "boot_ts": now,
            "last_analysis_ts": 0, "last_verdict": "MAI ANALIZZATO", "consecutive_no_edge": 0, "metrics": {}}


def coverage():
    tw = set(); tc = set()
    for f in glob.glob("data/raw/whales/backfill_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                try:
                    d = json.loads(l)
                    if d.get("usd"): tw.add(d["pool"])
                except: pass
        except: pass
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("tf") == "hour": tc.add(d["pool"])
        except: pass
    return len(tw), len(tc)


def write_state_md(state, directives, metrics):
    phase = state["current_phase"]
    since_a = (now - state["last_analysis_ts"]) / 3600 if state["last_analysis_ts"] else None
    gaps = directives.get("directives", []) if directives else []
    hi = [g for g in gaps if g.get("priority") == "HIGH"]
    tw, tc = state["metrics"].get("token_whale", 0), state["metrics"].get("token_candele", 0)
    L = [f"# 🐋 WHALE-RADAR — pannello di stato",
         f"*aggiornato {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}*", "",
         f"## Fase corrente: **{phase}**",
         f"- Ciclo #{state['cycle_id']}",
         f"- Ultima analisi: {('%.1f h fa' % since_a) if since_a is not None else 'mai'}",
         f"- Ultimo verdetto: **{state['last_verdict']}**", "",
         "## Cosa stiamo facendo ORA (Fase 1 = accumulo)"]
    if hi:
        L.append(f"Colmiamo i gap che l'analisi ha trovato — priorita' ALTA:")
        for g in hi[:6]:
            L.append(f"- {g['reason']}")
    else:
        L.append("- Accumulo largo dell'universo memecoin (nessun gap critico aperto).")
    L += ["", "## Metriche",
          f"- Balene: **{state['metrics'].get('whales','?')}** | wallet: {state['metrics'].get('wallets','?')}",
          f"- Token con balene: **{tw}** | token con candele: **{tc}**",
          f"- Gap aperti: {len(gaps)}", "",
          f"## Prossima analisi tra ~{max(0, ANALYSIS_EVERY_H - (since_a or 0)):.1f}h",
          "", "> Regola: nessun numero e' affidabile finche' non e' su 40+ token diversi. Zero soldi reali finche' l'edge non e' provato."]
    open("STATE.md", "w").write("\n".join(L))


def main():
    state = load_state()
    since = (now - state["last_analysis_ts"]) / 3600 if state["last_analysis_ts"] else 9999

    ran = False
    if since >= ANALYSIS_EVERY_H:
        # ---- FASE 2: analisi ----
        state["current_phase"] = "ANALISI"
        try:
            analyst_core.main()
            m = json.load(open("metrics.json"))
            state["last_analysis_ts"] = now
            state["last_verdict"] = m.get("verdict", "?")
            state["cycle_id"] += 1
            if not m.get("edge_found"): state["consecutive_no_edge"] = state.get("consecutive_no_edge", 0) + 1
            else: state["consecutive_no_edge"] = 0
            ran = True
        except Exception as e:
            print("analisi fallita:", str(e)[:120], flush=True)
        # ---- torna a FASE 1 ----
        state["current_phase"] = "ACCUMULO"

    tw, tc = coverage()
    state["metrics"].update({"token_whale": tw, "token_candele": tc})
    # whales/wallets totali
    try:
        m = json.load(open("metrics.json")) if os.path.exists("metrics.json") else {}
        state["metrics"]["whales"] = m.get("whales", state["metrics"].get("whales", "?"))
    except: pass
    directives = json.load(open("directives.json")) if os.path.exists("directives.json") else {"directives": []}

    json.dump(state, open(STATE, "w"), indent=1)
    write_state_md(state, directives, state["metrics"])
    print(f"DIRECTOR | fase={state['current_phase']} ciclo={state['cycle_id']} analisi_ora={ran} verdetto={state['last_verdict']} | token_whale={tw} token_candele={tc}", flush=True)


if __name__ == "__main__":
    main()
