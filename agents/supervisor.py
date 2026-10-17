#!/usr/bin/env python3
"""
SUPERVISOR — il GUARDIANO auto-riparante del loop. Ogni ora:
1. Scopre DINAMICAMENTE tutti i reparti (workflow) -> i nuovi sono coperti in automatico, senza toccare codice.
2. Per ognuno controlla l'ultimo run. Se e' FERMO (nessun successo da troppo) o CANCELLATO -> lo RI-LANCIA da solo
   (auto-riavvio, con WR_PAT). Se l'ultimo run e' FAILURE (probabile bug) -> lo ri-lancia E manda mail di alert.
3. Scrive SUPERVISOR.md (stato + cosa ha riavviato). La macchina non si ferma.
Legge con GITHUB_TOKEN, ri-lancia con WR_PAT (il GITHUB_TOKEN non puo' ri-lanciare per la regola anti-ricorsione).
Gira a orario E a ogni fine reparto. €0.
"""
import urllib.request, json, os, time, glob, gzip

REPO = "nicolostancato-web/whale-radar"
MAX_AGE_H = 14          # nessun successo da >14h = fermo (finestra larga: GitHub schedula i cron in modo irregolare)
now = int(time.time())
READ = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
PAT = os.environ.get("WR_PAT") or READ


def api(path, method="GET", data=None, tok=None):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{path}",
        data=json.dumps(data).encode() if data else None,
        headers={"Authorization": f"token {tok or READ}", "Accept": "application/vnd.github+json", "User-Agent": "supervisor"}, method=method)
    r = urllib.request.urlopen(req, timeout=30)
    return json.load(r) if r.length != 0 and method == "GET" else None


def age_h(iso):
    return (now - time.mktime(time.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")) + time.timezone) / 3600


def main():
    problems, restarted, rows = [], [], []
    try:
        wfs = api("actions/workflows")["workflows"]
    except Exception as e:
        print("API workflows ko:", str(e)[:60]); return
    for w in wfs:
        if w.get("state") != "active": continue
        fn = w["path"].split("/")[-1]
        if fn == "supervisor.yml": continue
        try:
            runs = api(f"actions/workflows/{fn}/runs?per_page=8")["workflow_runs"]
        except Exception:
            rows.append((fn, "?", "⚠️ API")); continue
        if not runs:
            rows.append((fn, "mai", "⚪ mai girato")); continue
        last = runs[0]
        succ = next((r for r in runs if r["conclusion"] == "success"), None)
        sa = age_h(succ["run_started_at"]) if succ else 999
        status = last["conclusion"] or last["status"]
        act = ""
        # non toccare se sta girando ora
        if last["status"] in ("in_progress", "queued"):
            rows.append((fn, f"{sa:.1f}h", "🟢 in corso")); continue
        if last["conclusion"] == "failure":
            problems.append(f"{fn}: ultimo run FALLITO (probabile bug)"); act = "→ ri-lancio"
        elif sa > MAX_AGE_H or last["conclusion"] == "cancelled":
            restarted.append(f"{fn} (fermo da {sa:.1f}h)"); act = "→ ri-lancio (auto-heal)"
        if act:
            try:
                api(f"actions/workflows/{fn}/dispatches", "POST", {"ref": "main"}, tok=PAT)
            except Exception as e:
                act += f" [dispatch ko: {str(e)[:30]}]"
        st = "🔴 FALLITO" if last["conclusion"] == "failure" else ("🟠 riavviato" if act else "🟢 ok")
        rows.append((fn, f"{sa:.1f}h", st + (" " + act if act else "")))

    healthy = len(problems) == 0
    head = "🔴 UN REPARTO FALLISCE" if problems else ("🟠 riavviati reparti fermi" if restarted else "🟢 LOOP SANO")
    L = [f"# 🛡️ SUPERVISOR — guardiano auto-riparante", f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}*", "",
         f"## {head}", "", "| Reparto | Ultimo successo | Stato |", "|---|---|---|"]
    L += [f"| {fn.replace('.yml','')} | {a} | {s} |" for fn, a, s in sorted(rows)]
    if restarted: L += ["", "## Riavviati da solo (auto-heal)"] + [f"- {r}" for r in restarted]
    if problems: L += ["", "## ⚠️ Problemi (mail inviata)"] + [f"- {p}" for p in problems]
    open("SUPERVISOR.md", "w").write("\n".join(L))

    print(f"{head} | reparti {len(rows)} | riavviati {len(restarted)} | falliti {len(problems)}", flush=True)
    if not healthy:
        raise SystemExit(1)   # -> mail al proprietario (bug reale, non transitorio)


if __name__ == "__main__":
    main()
