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
# L'ELENCO NON SI SCRIVE PIU' A MANO (27/09). Qui c'erano QUATTRO corsie, scritte quando ce
# n'erano quattro. Oggi sono cinquantuno, comprese quelle che raccolgono i dati che non tornano —
# e il guardiano dichiarava che andava tutto bene guardandone quattro.
# Ora l'elenco si deduce dalla cartella dei workflow: una corsia nuova e' sorvegliata perche'
# ESISTE, non perche' qualcuno si e' ricordato di iscriverla. Vedi `agents/corsie.py`.
import corsie as _C                                            # noqa: E402

# le soglie storiche restano dove erano state scelte apposta; per tutte le altre vale il ritmo
# dichiarato nel loro cron, moltiplicato per tre
_STORICHE = {"engine": 90, "ricerca": 75, "loop0": 75, "sperimenti": 120}
CORSIE = {nome: (pref, file, _STORICHE.get(nome, tol))
          for nome, file, pref, tol in _C.elenco()}
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
    # LA RETE DEI GUARDIANI (30/09): la stessa funzione la chiamano sentinella e questo.
    # Basta che UNO dei due sia vivo perche' l'altro torni. Un guardiano solo, per quanto
    # buono, e' un punto singolo di rottura — e oggi ha taciuto per cinque ore.
    try:
        from rianima import tutto as _controlla
        for riga in _controlla():
            print(f"HEARTBEAT | {riga}", flush=True)
    except Exception as e:
        print(f"HEARTBEAT | non ho potuto controllare le corsie ferme: {type(e).__name__}",
              flush=True)
    # LA FINESTRA SI MISURA IN TEMPO, NON IN NUMERO DI COMMIT (1/10). Qui si guardavano gli
    # ultimi 100 commit e si cercava dentro il prefisso di ogni corsia. Oggi ho pubblicato
    # correzioni a quaranta e cinquanta file per volta: i miei commit hanno RIEMPITO quella
    # finestra e spinto fuori quelli delle corsie, che sono quindi state dichiarate tutte mute
    # e rilanciate tutte insieme — tre ondate di sette corsie in otto minuti, ognuna che
    # annullava la precedente.
    # La mia attivita' generava la raffica che stavo cercando di spegnere.
    # IN POSITIVO: si chiedono i commit da UNA DATA — il doppio del silenzio piu' lungo
    # tollerato — cosi' la finestra non si stringe quando qualcun altro scrive molto. Una
    # finestra che cambia ampiezza in base a quanto parlano gli altri non e' una misura.
    ore = max(2.0, 2 * max(l for _, _, l in CORSIE.values()) / 60.0)
    da = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - ore * 3600))
    try:
        commits = gh(f"https://api.github.com/repos/{REPO}/commits"
                     f"?per_page=100&since={da}")
        # se la finestra e' piena fino all'orlo, non si sa cosa c'e' SOTTO: guardia cieca
        if len(commits) >= 100:
            print(f"HEARTBEAT | cento commit in {ore:.0f} ore: la finestra e' piena e non so "
                  f"cosa c'e' sotto. NON rilancio niente alla cieca.", flush=True)
            commits = []
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
