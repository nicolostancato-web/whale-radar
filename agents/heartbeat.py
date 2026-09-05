#!/usr/bin/env python3
"""
HEARTBEAT — il guardiano DEL MOTORE, e vive FUORI dal motore.

Il punto cieco piu' grave che avevamo: tutto il team dipende dal motore, ma nessuno controllava il motore
stesso. Il 30/08 ha girato 2h23 senza committare nulla e ce ne siamo accorti solo perche' un umano ha
guardato. Un guardiano che sta DENTRO la cosa che deve sorvegliare non serve a niente: se si blocca quella,
si blocca lui.

Questo gira in un workflow SEPARATO ogni 2h e fa una sola domanda: **il motore ha committato di recente?**
Se no, lo ri-lancia da solo. Scrive HEARTBEAT.md. €0.
"""
import json, os, time, urllib.request

REPO = "nicolostancato-web/whale-radar"
LIMITE_MIN = 90          # il motore committa a ogni ciclo (~30 min): oltre 90 min di silenzio e' anomalo
now = int(time.time())
TOK = os.environ.get("WR_PAT") or os.environ.get("GITHUB_TOKEN", "")


def gh(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method,
                                 data=json.dumps(data).encode() if data else None,
                                 headers={"Accept": "application/vnd.github+json",
                                          "Authorization": f"token {TOK}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
        return json.loads(b) if b else {}


def main():
    silenzio = None; ultimo = "?"
    try:
        commits = gh(f"https://api.github.com/repos/{REPO}/commits?per_page=20")
        for c in commits:
            msg = c["commit"]["message"].split("\n")[0]
            if msg.startswith("engine "):
                t = time.strptime(c["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")
                silenzio = (now - time.mktime(t)) / 60
                ultimo = msg
                break
    except Exception as e:
        silenzio = None

    azione = "—"
    if silenzio is None:
        stato = "❓ non riesco a leggere i commit del motore"
    elif silenzio > LIMITE_MIN:
        stato = f"🔴 **MOTORE FERMO** — nessun commit da **{silenzio:.0f} minuti**"
        try:
            attivi = gh(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=10")["workflow_runs"]
            vivo = [r for r in attivi if r["name"] == "engine" and r["status"] in ("in_progress", "queued")]
            gh(f"https://api.github.com/repos/{REPO}/actions/workflows/engine.yml/dispatches", "POST", {"ref": "main"})
            azione = ("ri-lanciato il motore" if not vivo else
                      "ri-lanciato il motore (ce n'era uno in corso ma muto: probabilmente bloccato)")
        except Exception as e:
            azione = f"non sono riuscito a ri-lanciarlo: {type(e).__name__}"
    else:
        stato = f"🟢 **MOTORE VIVO** — ultimo commit {silenzio:.0f} minuti fa"

    L = ["# 💓 HEARTBEAT — il motore è vivo?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · controllo ogni 2h, da FUORI il motore*", "",
         f"## {stato}", "",
         f"- ultimo commit del motore: `{ultimo}`",
         f"- soglia di allarme: **{LIMITE_MIN} minuti** di silenzio (il motore committa a ogni ciclo, ~30 min)",
         f"- azione presa: **{azione}**", "",
         "> **Perché vive fuori dal motore:** un guardiano che sta dentro la cosa che deve sorvegliare si blocca",
         "> insieme a lei. Il 30/08 il motore ha girato 2h23 senza committare e nessuno se n'è accorto: se ne è",
         "> accorto un umano. Da adesso se ne accorge questo, e lo riavvia da solo."]
    open("HEARTBEAT.md", "w").write("\n".join(L))
    print(f"HEARTBEAT | {stato[:40]} | {azione}", flush=True)


if __name__ == "__main__":
    main()
