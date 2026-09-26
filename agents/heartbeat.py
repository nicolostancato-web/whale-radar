#!/usr/bin/env python3
"""
HEARTBEAT — il guardiano DI TUTTE LE CORSIE, e vive FUORI da ognuna.

Il punto cieco piu' grave che avevamo: tutto dipendeva dal motore, ma nessuno controllava il motore
stesso. Il 30/08 ha girato 2h23 senza committare nulla e ce ne siamo accorti solo perche' un umano ha
guardato. Un guardiano che sta DENTRO la cosa che deve sorvegliare non serve a niente: se si blocca
quella, si blocca lui.

09/09 — ORA SONO QUATTRO. Sorvegliava solo il motore, mentre le corsie sono diventate quattro:
motore (accumulo), ricerca (la percentuale), loop 0 (l'ispezione) e sperimenti (le idee). Un
guardiano che copre una corsia su quattro da' la sensazione della sorveglianza senza la sorveglianza,
ed e' peggio di nessun guardiano: si smette di guardare a mano perche' "tanto c'e' lui".
Riparare dove ho visto il problema e non dove il problema puo' stare e' come non ripararlo.

Ogni corsia ha la sua soglia, perche' committano a ritmi diversi. Se una tace oltre la sua soglia,
questo la ri-lancia da sola. Scrive HEARTBEAT.md. €0.
"""
import calendar, json, os, time, urllib.request

REPO = "nicolostancato-web/whale-radar"
# corsia -> (prefisso del suo commit, file del workflow, minuti di silenzio tollerati)
# Le soglie sono diverse perche' i ritmi sono diversi: una soglia sola sarebbe sbagliata due volte,
# troppo nervosa per chi e' lento e troppo paziente per chi e' veloce.
CORSIE = {
    "motore":     ("engine ",     "engine.yml",     90),
    "ricerca":    ("ricerca ",    "ricerca.yml",    75),
    "loop 0":     ("loop0 ",      "loop0.yml",      75),
    "sperimenti": ("sperimenti ", "sperimenti.yml", 120),
}
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
    try:
        commits = gh(f"https://api.github.com/repos/{REPO}/commits?per_page=100")
    except Exception:
        commits = []
    try:
        attivi = gh(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=30")["workflow_runs"]
    except Exception:
        attivi = []

    # NON SAPERE NON E' SAPERE CHE E' MORTA (09/09). Se non riesco a leggere i commit — token
    # assente, rete giu', limite di chiamate — la lista arriva vuota e senza questo controllo il
    # guardiano concludeva "nessun commit, quindi ferma" e riaccendeva tutte e quattro le corsie.
    # Un guardiano cieco che spinge bottoni fa piu' danni di un guardiano spento.
    if not commits:
        open("HEARTBEAT.md", "w").write(
            "# 💓 HEARTBEAT\n\n## ❓ Non riesco a leggere i commit\n\n"
            "> Non tocco niente: **non sapere se una corsia e' viva non e' sapere che e' morta**.\n"
            "> Riaccendere alla cieca e' un danno, non una precauzione.\n")
        print("HEARTBEAT | non riesco a leggere i commit: non tocco niente", flush=True)
        return

    righe = []
    for nome, (prefisso, wf, limite) in CORSIE.items():
        silenzio, ultimo = None, "?"
        for c in commits:
            msg = c["commit"]["message"].split("\n")[0]
            if msg.startswith(prefisso):
                tt = time.strptime(c["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")
                # calendar.timegm e NON time.mktime: mktime legge la data come ora LOCALE, e su una
                # macchina non in UTC il guardiano vedeva due ore di silenzio inventate e
                # riaccendeva corsie vive. Un guardiano che dipende dal fuso non e un guardiano.
                silenzio = (now - calendar.timegm(tt)) / 60
                ultimo = msg
                break
        azione = "—"
        if silenzio is None:
            # NIENTE COMMIT NELLE ULTIME 100 RIGHE: o e' ferma da tanto, o non ha mai girato.
            # In entrambi i casi la si accende: riaccendere una corsia viva non fa danno, la
            # concorrenza del workflow tiene una sola corsa per gruppo.
            stato = "❓ nessun commit recente"
            try:
                gh(f"https://api.github.com/repos/{REPO}/actions/workflows/{wf}/dispatches",
                   "POST", {"ref": "main"})
                azione = "accesa"
            except Exception as e:
                azione = f"non sono riuscito ad accenderla: {type(e).__name__}"
        elif silenzio > limite:
            stato = f"🔴 **FERMA** — muta da **{silenzio:.0f} min** (soglia {limite})"
            vivo = [r for r in attivi if r["name"] == wf[:-4] and r["status"] in ("in_progress", "queued")]
            try:
                gh(f"https://api.github.com/repos/{REPO}/actions/workflows/{wf}/dispatches",
                   "POST", {"ref": "main"})
                azione = ("ri-lanciata" if not vivo else
                          "ri-lanciata (ce n'era una in corso ma muta: probabilmente bloccata)")
            except Exception as e:
                azione = f"non sono riuscito a ri-lanciarla: {type(e).__name__}"
        else:
            stato = f"🟢 viva — ultimo commit {silenzio:.0f} min fa"
        righe.append((nome, stato, ultimo, azione, limite))

    vive = sum(1 for r in righe if r[1].startswith("🟢"))
    L = ["# 💓 HEARTBEAT — le quattro corsie sono vive?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · controllo da FUORI ogni corsia*", "",
         f"## {vive}/4 vive", "",
         "| corsia | stato | ultimo commit | azione |", "|---|---|---|---|"]
    L += [f"| **{n}** | {s} | `{u[:42]}` | {a} |" for n, s, u, a, _ in righe]
    L += ["", "> **Perché vive fuori:** un guardiano che sta dentro la cosa che deve sorvegliare si",
          "> blocca insieme a lei. Il 30/08 il motore ha girato 2h23 senza committare e se n'è accorto",
          "> un umano; da allora se ne accorge questo.", "",
          "> **Perché adesso sono quattro:** sorvegliava solo il motore mentre le corsie diventavano",
          "> quattro. Un guardiano che ne copre una su quattro dà la sensazione della sorveglianza",
          "> senza la sorveglianza — ed è peggio di nessun guardiano, perché si smette di controllare",
          "> a mano «tanto c'è lui».", "",
          "> **Chi spegne qualcosa ha il dovere di riaccenderla**: qui nessuno spegne, ma chi trova",
          "> una corsia muta la riaccende invece di limitarsi a scriverlo."]
    open("HEARTBEAT.md", "w").write("\n".join(L))
    print(f"HEARTBEAT | {vive}/4 corsie vive", flush=True)


if __name__ == "__main__":
    main()
