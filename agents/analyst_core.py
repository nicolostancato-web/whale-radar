#!/usr/bin/env python3
"""
ANALYST_CORE — cervello della FASE 2. Analizza i dati accumulati, cerca l'edge in modo RIGOROSO
(survivorship-corretto, con trasparenza su quanti TOKEN diversi), e RILEVA I GAP di dati da colmare.
Scrive: analysis_report.md (leggibile), metrics.json (per il director), directives.json (ordini per la Fase 1).
Nessuna chiamata esterna: solo Python sui nostri file. €0. Deterministico.
"""
import gzip, json, glob, os, time, statistics as st
from collections import defaultdict, Counter

HORIZONS = (24, 72, 168)
MIN_TOKENS = 40          # sotto questo n. di token diversi, un numero e' aneddoto (non fidarsi)
ENTRY_DELAY_H = 1        # entro 1h dopo il buy della balena
now = int(time.time())


def load_candles():
    cand = {}
    for f in glob.glob("data/raw/candles/*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("tf") == "hour":
                    cand.setdefault(d["pool"], {})[int(d["ts"])] = (d["cl"], d.get("v", 0))
        except EOFError: pass
    for p in cand: cand[p] = dict(sorted(cand[p].items()))
    return cand


def load_whales():
    w = []
    for f in glob.glob("data/raw/whales/backfill_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                try:
                    d = json.loads(l)
                    if d.get("usd") and d.get("ts"): w.append(d)
                except: pass
        except EOFError: pass
    return w


def main():
    cand = load_candles()
    whales = [x for x in load_whales() if x["pool"] in cand]
    last_ts = {p: max(ks) for p, ks in cand.items() if ks}

    def price(p, ts):
        ks = cand[p]; b = None
        for k in ks:
            if k <= ts + 1800: b = k
            else: break
        return ks[b] if b is not None and abs(b - ts) <= 6 * 3600 else None

    def slippage(vol):   # round-trip stimato per lato, per liquidita' (volume candela d'entrata)
        if vol < 10000: return 0.30
        if vol < 100000: return 0.10
        return 0.05

    # simulazione per orizzonte, SURVIVORSHIP-CORRETTA
    sims = {}
    for H in HORIZONS:
        trades = []
        for x in whales:
            p = x["pool"]; e = price(p, x["ts"] + ENTRY_DELAY_H * 3600)
            if not e or e[0] <= 0: continue
            entry, vol = e
            tgt = x["ts"] + (ENTRY_DELAY_H + H) * 3600
            ex = price(p, tgt)
            if ex is None:
                # nessuna candela vicino al target: se il target e' nel PASSATO ed il pool e' morto -> perdita
                if tgt < now and last_ts.get(p, 0) < tgt - 3600:
                    exitp = cand[p][last_ts[p]][0]
                else:
                    continue   # target nel futuro: non misurabile
            else:
                exitp = ex[0]
            s = slippage(vol)
            gross = exitp / entry - 1
            net = (exitp * (1 - s)) / (entry * (1 + s)) - 1
            trades.append({"pool": p, "wallet": x["wallet"], "usd": x["usd"], "tag": x.get("tag"),
                           "gross": gross, "net": net, "dead": exitp <= entry * 0.02})
        sims[H] = trades

    def agg(trades, key="net"):
        if not trades: return None
        r = [t[key] for t in trades]
        ntok = len(set(t["pool"] for t in trades))
        return {"n_trades": len(r), "n_token": ntok, "n_wallet": len(set(t["wallet"] for t in trades)),
                "mean": round(st.mean(r), 4), "median": round(st.median(r), 4),
                "win_rate": round(sum(1 for x in r if x > 0) / len(r), 3),
                "x2": sum(1 for x in r if x >= 1), "x3": sum(1 for x in r if x >= 2), "x5": sum(1 for x in r if x >= 4),
                "dead": sum(1 for t in trades if t["dead"]), "best": round(max(r), 2), "worst": round(min(r), 2),
                "affidabile": ntok >= MIN_TOKENS}

    results = {H: {"tutti": agg(sims[H])} for H in HORIZONS}

    # ---- RILEVAMENTO GAP (deterministico) ----
    gaps = []
    tokens_whale = set(x["pool"] for x in whales)
    # gap 1: token con balena ma poche candele (AGGREGATO in una directive)
    poche = [p for p in tokens_whale if len(cand.get(p, {})) < 72]
    if poche:
        gaps.append({"action": "fetch_candles", "target": "MULTI", "params": {"pools": poche[:200], "hours": 1000},
                     "reason": f"{len(poche)} token con balena hanno <72 candele orarie -> scaricare piu' candele", "priority": "HIGH"})
    # gap 2 (IL PIU' IMPORTANTE): diversita' per la finestra multi-giorno
    for H in HORIZONS:
        a = results[H]["tutti"]
        ntok = a["n_token"] if a else 0
        if ntok < MIN_TOKENS:
            gaps.append({"action": "need_diversity", "target": f"{H}h", "params": {"have": ntok, "need": MIN_TOKENS},
                         "reason": f"finestra {H}h misurabile su solo {ntok} token diversi (<{MIN_TOKENS}): serve tempo+piu' token",
                         "priority": "HIGH" if H == 24 else "MEDIUM"})
    # gap 3: wallet con pochi acquisti (campione insufficiente per giudicarli)
    wc = Counter(x["wallet"] for x in whales)
    thin = sum(1 for v in wc.values() if v < 4)
    if thin: gaps.append({"action": "accumulate_whales", "target": "wallet_history",
                          "params": {"thin_wallets": thin}, "reason": f"{thin} wallet con <4 acquisti: piu' whale per giudicarli", "priority": "MEDIUM"})

    # ---- VERDETTO (onesto) ----
    a24 = results[24]["tutti"]
    if not a24 or not a24["affidabile"]:
        verdict = "DATI INSUFFICIENTI"
        verdict_note = f"campione troppo poco diverso (24h su {a24['n_token'] if a24 else 0} token, servono {MIN_TOKENS}+). Nessun numero e' affidabile."
        edge_found = False
    else:
        net = a24["mean"]
        if net > 0.05 and a24["win_rate"] > 0.5:
            verdict = "EDGE POSSIBILE"; edge_found = True
        elif net > 0: verdict = "EDGE DEBOLE"; edge_found = False
        else: verdict = "NESSUN EDGE"; edge_found = False
        verdict_note = f"rendimento netto medio 24h {net*100:+.1f}% su {a24['n_token']} token, win {a24['win_rate']*100:.0f}%"

    # ---- OUTPUT ----
    metrics = {"ts": now, "verdict": verdict, "edge_found": edge_found, "n_gap": len(gaps),
               "results": results, "tokens_whale": len(tokens_whale), "whales": len(whales)}
    json.dump(metrics, open("metrics.json", "w"), indent=0)
    json.dump({"generated_at": now, "generator": "analyst_core", "directives": gaps}, open("directives.json", "w"), indent=1)

    # report leggibile
    R = [f"# ANALISI FASE-2 — {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}", "",
         f"**Verdetto: {verdict}** — {verdict_note}", "",
         "## Risultati per finestra (netti di slippage, survivorship-corretti)",
         "| Finestra | n_trade | **n_token** | netto medio | mediana | %win | 2x+ | 5x+ | morti | affidabile? |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for H in HORIZONS:
        a = results[H]["tutti"]
        if a:
            R.append(f"| {H}h | {a['n_trades']} | **{a['n_token']}** | {a['mean']*100:+.1f}% | {a['median']*100:+.1f}% | {a['win_rate']*100:.0f}% | {a['x2']} | {a['x5']} | {a['dead']} | {'SI' if a['affidabile'] else 'NO (aneddoto)'} |")
        else:
            R.append(f"| {H}h | 0 | 0 | - | - | - | - | - | - | NO |")
    R += ["", f"> Ogni numero e' calcolato sul n. di TOKEN diversi indicato. Sotto {MIN_TOKENS} token = aneddoto, non fidarsi.", "",
          "## Gap di dati rilevati (ordini per la Fase 1)"]
    for g in gaps:
        R.append(f"- **[{g['priority']}]** {g['reason']}")
    if not gaps: R.append("- Nessun gap critico.")
    open("analysis_report.md", "w").write("\n".join(R))

    print(f"ANALISI FATTA | {verdict} | gap={len(gaps)} | 24h su {a24['n_token'] if a24 else 0} token", flush=True)


if __name__ == "__main__":
    main()
