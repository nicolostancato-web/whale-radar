#!/usr/bin/env python3
"""
TEAM · SECURITY — il ruolo che tiene le spalle agli altri mentre corrono.

Il repo e' PUBBLICO: chiunque legge tutto. Un loop che lavora da solo e committa ogni 30 minuti puo'
scrivere per sbaglio una chiave dentro un file di stato, o un log. Quel giorno la chiave e' bruciata e
il danno e' immediato. Questo ruolo controlla, a ogni riunione, che non sia successo.
Scrive SECURITY.md · sola lettura · €0.
"""
import json, os, re, glob, time

now = int(time.time())
# firme di segreti veri (non parole generiche: qui i falsi allarmi fanno perdere fiducia nel controllo)
FIRME = [
    (r"ghp_[A-Za-z0-9]{30,}", "token GitHub"),
    (r"github_pat_[A-Za-z0-9_]{50,}", "token GitHub (nuovo formato)"),
    (r"sk-ant-[A-Za-z0-9\-_]{30,}", "chiave Anthropic"),
    (r"sk-[A-Za-z0-9]{40,}", "chiave OpenAI"),
    (r"sb_secret_[A-Za-z0-9_\-]{20,}", "service key Supabase"),
    (r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}", "JWT"),
    (r"AIza[A-Za-z0-9_\-]{30,}", "chiave Google"),
    # un UUID nudo NO: e' ovunque (path, id di build) e un controllo che grida al lupo non lo guarda piu'
    # nessuno. Lo segnaliamo solo se sta accanto a una parola che lo qualifica come credenziale.
    (r"(?i)(token|api[_-]?key|secret|password)\W{0,4}[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
     "token in formato UUID"),
]
SALTA = (".git/", "__pycache__", ".pyc", "data/multichain/", "data/raw/", ".jsonl.gz")


def scansiona():
    trovati = []
    for f in glob.glob("**/*", recursive=True):
        if not os.path.isfile(f) or any(s in f for s in SALTA): continue
        if os.path.getsize(f) > 2_000_000: continue
        if f.endswith((".gz", ".png", ".jpg", ".pdf", ".zip")): continue
        try: txt = open(f, "r", errors="ignore").read()
        except Exception: continue
        for pat, nome in FIRME:
            for m in re.finditer(pat, txt):
                v = m.group(0)
                if "${{" in txt[max(0, m.start()-30):m.start()]: continue      # e' un secret di Actions: ok
                trovati.append((f, nome, v[:8] + "…"))
    return trovati


def controlla_workflow():
    """i workflow devono prendere le chiavi dai SECRET, mai scriverle in chiaro."""
    problemi = []
    for f in glob.glob(".github/workflows/*.yml"):
        txt = open(f, errors="ignore").read()
        for pat, nome in FIRME[:5]:
            if re.search(pat, txt): problemi.append((os.path.basename(f), f"{nome} scritta in chiaro"))
        if "pull_request_target" in txt:
            problemi.append((os.path.basename(f), "usa pull_request_target: un PR esterno potrebbe leggere i secret"))
    return problemi


def main():
    segreti = scansiona()
    wf = controlla_workflow()
    tot = len(segreti) + len(wf)
    verdetto = ("🟢 **PULITO** — nessuna credenziale esposta nel repo pubblico" if tot == 0 else
                "🔴 **ALLARME** — c'e' qualcosa che non deve stare in un repo pubblico")
    L = ["# 🔒 TEAM · SECURITY",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · il repo e' PUBBLICO: chiunque legge tutto*", "",
         f"## {verdetto}", ""]
    if segreti:
        L += ["| file | cosa | inizio |", "|---|---|---|"]
        L += [f"| `{f}` | {n} | `{v}` |" for f, n, v in segreti[:20]]
        L += ["", "> **Da fare subito:** revocare la chiave, toglierla dal file, ri-generarla. Una chiave finita",
              "> in un repo pubblico va considerata bruciata anche se la cancelli: la storia resta.", ""]
    if wf:
        L += ["### Workflow", ""] + [f"- `{a}`: {b}" for a, b in wf] + [""]
    if tot == 0:
        L += ["**Controlli passati:**", "",
              "- nessun token GitHub / Anthropic / OpenAI / Supabase / Google in chiaro nei file",
              "- nessun JWT nei file versionati",
              "- i workflow prendono le credenziali dai secret di GitHub, non dal codice",
              "- nessun workflow usa `pull_request_target` (che esporrebbe i secret a PR esterni)", ""]
    L += ["> Il team corre veloce e committa ogni 30 minuti: questo ruolo esiste perche' un segreto",
          "> scritto per sbaglio, in un repo pubblico, e' bruciato nel momento stesso in cui viene pushato."]
    open("SECURITY.md", "w").write("\n".join(L))
    json.dump({"ts": now, "problemi": tot}, open("data/security_flags.json", "w"))
    print(f"SECURITY | {verdetto[:30]} | {tot} problemi", flush=True)


if __name__ == "__main__":
    main()
