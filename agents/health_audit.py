#!/usr/bin/env python3
"""
HEALTH_AUDIT — il watchdog dei DATI/LOGICA (non solo dei workflow). Gira ogni 3h in parallelo e controlla la
SALUTE VERA della pipeline: copertura trade pre-entrata per chain, crescita dei dati (qualcosa e' fermo?),
freschezza dei numeri, anomalie. Se trova problemi li SEGNALA in HEALTH_AUDIT.md con 🔴. Cosi' i bug/dati-rotti
NON restano nascosti finche' Nicolo chiede "news?": vengono flaggati da soli. Alcune cose le auto-ripara (rilancia
un collector fermo via workflow dispatch, se WR_PAT c'e'). Confronto storico in data/audit_history.jsonl. €0.
"""
import gzip, json, glob, os, time, urllib.request, statistics as st

now = int(time.time())
CHAINS = ["solana", "bsc", "base"]
HIST = "data/audit_history.jsonl"
REPO = "nicolostancato-web/whale-radar"


def chain_health(ch):
    """ritorna metriche di salute di una chain: token usabili, % con trade, % con dati PRE-ENTRATA."""
    usable = 0; with_trades = 0; pre_ok = 0
    for cf in glob.glob(f"data/multichain/{ch}/candles/*.jsonl.gz"):
        addr = cf.split("/")[-1].replace(".jsonl.gz", "")
        try:
            cs = sorted(int(json.loads(l)["ts"]) for l in gzip.open(cf, "rt") if json.loads(l).get("cl"))
            if len(cs) < 5: continue
            usable += 1
            ent = cs[0] + 1 * 3600
            tf = f"data/multichain/{ch}/trades/{addr}.jsonl.gz"
            if os.path.exists(tf):
                with_trades += 1
                pre = sum(1 for l in gzip.open(tf, "rt") if json.loads(l).get("ts", 0) <= ent)
                if pre >= 2: pre_ok += 1
        except: pass
    return {"usable": usable, "with_trades": with_trades, "pre_ok": pre_ok,
            "pre_pct": round(pre_ok / usable * 100) if usable else 0}


def dispatch(wf, pat):
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/actions/workflows/{wf}/dispatches",
            data=json.dumps({"ref": "main"}).encode(),
            headers={"Authorization": f"token {pat}", "Accept": "application/vnd.github+json"}, method="POST")
        urllib.request.urlopen(req, timeout=20); return True
    except: return False


def main():
    prev = None
    if os.path.exists(HIST):
        lines = [l for l in open(HIST) if l.strip()]
        if lines: prev = json.loads(lines[-1])

    cur = {"date": time.strftime("%Y-%m-%d %H:%MZ", time.gmtime(now)), "ts": now, "chains": {}}
    problems = []; actions = []
    for ch in CHAINS:
        h = chain_health(ch); cur["chains"][ch] = h
        # 🔴 copertura pre-entrata bassa (feature forti cieche)
        if h["usable"] >= 30 and h["pre_pct"] < 30:
            problems.append(f"🔴 **{ch}**: solo {h['pre_pct']}% dei token ha dati PRE-ENTRATA ({h['pre_ok']}/{h['usable']}) → feature forti cieche, la MEDIA non e' affidabile")
        # 🔴 crescita ferma (collector bloccato)
        if prev and ch in prev.get("chains", {}):
            if h["usable"] <= prev["chains"][ch]["usable"] and h["with_trades"] <= prev["chains"][ch]["with_trades"]:
                problems.append(f"🟠 **{ch}**: dati FERMI da 3h (usable {h['usable']}, trade {h['with_trades']}) → collector forse bloccato")

    # freschezza numeri chiave
    for fn, label in [("EDGE.md", "Robinhood"), ("MULTICHAIN.md", "multichain")]:
        if os.path.exists(fn):
            age_h = (now - int(os.path.getmtime(fn))) / 3600
            if age_h > 30: problems.append(f"🟠 **{label}** ({fn}): non aggiornato da {age_h:.0f}h")

    # auto-riparazione: se un collector sembra fermo, rilancialo
    pat = os.environ.get("WR_PAT", "")
    if pat:
        for p in problems:
            if "collector forse bloccato" in p and "solana" in p:
                if dispatch("solana_helius.yml", pat): actions.append("rilanciato solana_helius")

    hist = []
    if os.path.exists(HIST):
        for l in open(HIST):
            try: hist.append(json.loads(l))
            except: pass
    hist.append(cur); hist = hist[-200:]
    with open(HIST, "w") as fo:
        for d in hist: fo.write(json.dumps(d) + "\n")

    L = [f"# 🛡️ HEALTH AUDIT — watchdog dati/logica",
         f"*{cur['date']} · controllo automatico ogni 3h*", "",
         (f"## 🔴 {len(problems)} PROBLEMI RILEVATI" if problems else "## 🟢 TUTTO SANO — nessun problema rilevato"), ""]
    for p in problems: L.append(f"- {p}")
    if actions: L += ["", "## Auto-riparazioni fatte:"] + [f"- ✅ {a}" for a in actions]
    L += ["", "## Copertura dati per chain",
          "| chain | token usabili | con trade | con dati PRE-ENTRATA |", "|---|---|---|---|"]
    for ch in CHAINS:
        h = cur["chains"][ch]
        L.append(f"| {ch} | {h['usable']} | {h['with_trades']} | **{h['pre_pct']}%** ({h['pre_ok']}) |")
    L += ["", "> Se qui c'e' un 🔴/🟠, il problema e' gia' noto (non serve che lo scopra Nicolo chiedendo 'news?')."]
    open("HEALTH_AUDIT.md", "w").write("\n".join(L))
    print(f"HEALTH_AUDIT | {len(problems)} problemi | " + " ".join(f"{ch}:{cur['chains'][ch]['pre_pct']}%pre" for ch in CHAINS), flush=True)


if __name__ == "__main__":
    main()
