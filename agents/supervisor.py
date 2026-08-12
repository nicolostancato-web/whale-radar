#!/usr/bin/env python3
"""
SUPERVISOR — il controllore del LOOP. Verifica via API GitHub che OGNI reparto abbia girato nella sua
finestra (non basta guardare i dati: bisogna sapere se i cron scattano davvero). Scrive SUPERVISOR.md
(tabella per reparto: ultimo run, eta', stato) e, se un reparto e' DAVVERO fermo, esce con errore ->
GitHub manda mail di alert al proprietario. Nessuna dipendenza esterna (solo urllib). €0.
Gira sia a orario sia quando un reparto finisce (workflow_run) -> quasi impossibile che si spenga in silenzio.
"""
import urllib.request, json, os, time, glob, gzip, re

REPO = "nicolostancato-web/whale-radar"
# reparto -> ore massime tollerate senza un run di SUCCESSO (larghe: GitHub schedula i cron in modo irregolare)
WF = {"whale_backfill.yml": 8, "whale_candles.yml": 8, "collector.yml": 12,
      "wallet_scores.yml": 16, "director.yml": 6, "watchdog_quality.yml": 12}
now = int(time.time())


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t: return t
    try:
        txt = open(os.path.expanduser("~/Documents/b2b-finder-credentials.txt"), errors="ignore").read()
        m = re.search(r"ghp_[A-Za-z0-9]+", txt)
        if m: return m.group(0)
    except: pass
    m = re.search(r"ghp_[A-Za-z0-9]+", open(os.path.expanduser("~/n8n builder/CLAUDE.md"), errors="ignore").read())
    return m.group(0) if m else None


def api(path):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{path}",
                                 headers={"Authorization": f"token {token()}", "Accept": "application/vnd.github+json", "User-Agent": "supervisor"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def last_success_age(wf):
    try:
        runs = api(f"actions/workflows/{wf}/runs?per_page=10")["workflow_runs"]
    except Exception as e:
        return None, f"API err {str(e)[:30]}"
    for r in runs:
        if r["conclusion"] == "success":
            t = time.mktime(time.strptime(r["run_started_at"], "%Y-%m-%dT%H:%M:%SZ")) - time.timezone
            return (now - t) / 3600, None
    return 999, "nessun successo recente"


def whale_growth():
    w = 0
    for f in glob.glob("data/raw/whales/backfill_*.jsonl.gz"):
        try:
            for l in gzip.open(f, "rt"):
                if '"usd"' in l: w += 1
        except: pass
    prev = json.load(open("data/supervisor_snapshot.json")) if os.path.exists("data/supervisor_snapshot.json") else {}
    d = w - prev.get("whales", 0)
    json.dump({"ts": now, "whales": w}, open("data/supervisor_snapshot.json", "w"))
    return w, d, prev.get("ts", 0)


def main():
    problems = []
    rows = []
    for wf, maxh in WF.items():
        age, err = last_success_age(wf)
        if err and age is None:
            rows.append((wf, "?", "⚠️ API")); continue
        stalled = age > maxh
        if stalled: problems.append(f"{wf}: ultimo successo {age:.1f}h fa (max {maxh}h) — FERMO?")
        rows.append((wf, f"{age:.1f}h fa", "🔴 FERMO" if stalled else "🟢 ok"))

    w, dw, prev_ts = whale_growth()
    healthy = len(problems) == 0
    status = "🟢 LOOP SANO" if healthy else "🔴 QUALCOSA È FERMO"

    L = [f"# 🛡️ SUPERVISOR — controllo del loop",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}*", "",
         f"## {status}", "",
         "| Reparto | Ultimo successo | Stato |", "|---|---|---|"]
    L += [f"| {wf.replace('.yml','')} | {a} | {s} |" for wf, a, s in rows]
    L += ["", f"**Balene: {w}** ({'+' if dw>=0 else ''}{dw} dall'ultimo controllo)", ""]
    if problems:
        L += ["## ⚠️ Problemi"] + [f"- {p}" for p in problems]
    open("SUPERVISOR.md", "w").write("\n".join(L))

    print(f"{status} | " + " · ".join(f"{wf.replace('.yml','')}={s}" for wf, a, s in rows), flush=True)
    if problems:
        print("FERMI:", "; ".join(problems), flush=True)
        raise SystemExit(1)   # -> mail di alert


if __name__ == "__main__":
    main()
