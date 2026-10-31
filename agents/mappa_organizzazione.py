"""La mappa di chi scrive cosa, dove e quando. Generata dalla REALTA', non dalle intenzioni.

PERCHE' ESISTE (10/10, diagnosi di Nicolo'): «se facciamo un sistema cosi' grosso l'AI sbaglia
comunque. C'e' sempre qualcosa. Bisogna schedularle le robe, dire esattamente cosa deve fare,
esattamente gli orari, esattamente dove deve scrivere. C'e' molta confusione, roba gira a caso.
L'abbiamo fatto troppo grosso.»

Ha ragione, e la causa e' precisa: nessuno ha mai DICHIARATO il contratto di ogni corsia. Senza
contratto non esiste la nozione di «sbagliato»: un file che nasce nel posto sbagliato, una corsia
che gira quando non serve, un dato riscritto da due corsie diverse non sono violazioni di niente,
quindi nessun controllo li puo' vedere. Gli audit finora guardavano i sintomi; questo guarda la
mappa.

Si parte dalla realta' e non dalle intenzioni: si leggono i file di corsia (quando gira, cosa
esegue) e i sorgenti (cosa scrivono), e si mette tutto in una tabella. Da quella tabella si vede
subito il disordine vero: chi scrive lo stesso file da due posti, chi gira senza che nessuno legga
quello che produce, chi non gira mai.
"""
import collections
import json
import os
import re
import sys

WF = ".github/workflows"
USCITA_MD = "ORGANIZZAZIONE.md"
USCITA_JSON = "data/organizzazione.json"


def _stato_corsie():
    """Chi e' accesa, chiesto a GitHub: e' lui l'autorita', non un nostro elenco."""
    tok = os.environ.get("WR_PAT") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        c = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
        if os.path.exists(c):
            m = re.search(r"ghp_[A-Za-z0-9]+", open(c, encoding="utf-8", errors="ignore").read())
            tok = m.group(0) if m else None
    if not tok:
        return {}
    import urllib.request
    try:
        r = urllib.request.Request(
            "https://api.github.com/repos/nicolostancato-web/whale-radar/"
            "actions/workflows?per_page=100", headers={"Authorization": f"token {tok}"})
        return {x["name"]: x["state"]
                for x in json.load(urllib.request.urlopen(r, timeout=60))["workflows"]}
    except Exception:
        return {}


def _scrive(sorgente):
    """I percorsi che un sorgente scrive, letti dalle sue costanti e dalle sue aperture."""
    if not os.path.exists(sorgente):
        return set()
    s = open(sorgente, encoding="utf-8", errors="replace").read()
    fuori = set()
    # costanti tipo ARCH = f"{BASE}/x.json", con BASE = data/multichain/<chain>
    base = "data/multichain/<chain>" if 'f"data/multichain/{CHAIN}"' in s else None
    for m in re.finditer(r'=\s*f?"([^"]*?(?:data|\.md|\.json|\.jsonl)[^"]*)"', s):
        v = m.group(1)
        if base:
            v = v.replace("{BASE}", base)
        v = re.sub(r"\{[^}]*\}", "<x>", v)
        if "/" in v or v.endswith((".md", ".json", ".jsonl")):
            fuori.add(v)
    for m in re.finditer(r'open\(\s*"([^"]+)"\s*,\s*"[wa]', s):
        fuori.add(m.group(1))
    return {x for x in fuori if not x.startswith("http")}


def main():
    stato = _stato_corsie()
    righe = []
    for f in sorted(os.listdir(WF)):
        if not f.endswith((".yml", ".yaml")):
            continue
        nome = f.rsplit(".", 1)[0]
        s = open(f"{WF}/{f}", encoding="utf-8", errors="replace").read()
        cron = re.findall(r'cron: *["\']([^"\']+)["\']', s)
        agenti = sorted(set(re.findall(r"agents/(\w+)\.py", s)))
        scrive = set()
        for a in agenti:
            scrive |= _scrive(f"agents/{a}.py")
        righe.append({
            "corsia": nome,
            "stato": stato.get(nome, "?"),
            "orologio": cron or [],
            "a_mano": "workflow_dispatch" in s,
            "agenti": agenti,
            "scrive": sorted(scrive)[:12],
            "consegna": ("allegato" if "upload-artifact" in s else
                         ("spinge" if "git push" in s else "NIENTE")),
        })
    acc = [r for r in righe if r["stato"] == "active"]
    print(f"MAPPA | {len(righe)} corsie in tutto, {len(acc)} accese\n")

    # IL DISORDINE VERO, in tre numeri
    chi_scrive = collections.defaultdict(set)
    for r in acc:
        for p in r["scrive"]:
            chi_scrive[p].add(r["corsia"])
    doppi = {p: c for p, c in chi_scrive.items() if len(c) > 1}
    senza_orologio = [r["corsia"] for r in acc if not r["orologio"]]
    senza_consegna = [r["corsia"] for r in acc if r["consegna"] == "NIENTE"]
    print(f"MAPPA | file scritti da PIU' di una corsia accesa: {len(doppi)}")
    for p, c in sorted(doppi.items())[:8]:
        print(f"   {p}  <-  {', '.join(sorted(c))}")
    print(f"\nMAPPA | corsie accese SENZA orologio (girano solo se qualcuno le chiama): "
          f"{len(senza_orologio)}")
    print("   " + ", ".join(sorted(senza_orologio)[:14]))
    print(f"\nMAPPA | corsie accese che non consegnano niente: {len(senza_consegna)}")
    print("   " + ", ".join(sorted(senza_consegna)[:14]))

    json.dump({"corsie": righe, "scritti_da_piu_corsie": {k: sorted(v) for k, v in doppi.items()}},
              open(USCITA_JSON, "w"), indent=1, sort_keys=True)

    with open(USCITA_MD, "w") as f:
        f.write("# Organizzazione: chi scrive cosa, dove e quando\n\n")
        f.write("*generato da `agents/mappa_organizzazione.py` leggendo i file di corsia e i "
                "sorgenti. Non e' una dichiarazione di intenti: e' quello che il sistema fa "
                "davvero oggi.*\n\n")
        f.write(f"**{len(righe)} corsie, {len(acc)} accese.** "
                f"{len(doppi)} file sono scritti da piu' di una corsia accesa, "
                f"{len(senza_orologio)} corsie accese non hanno un orologio, "
                f"{len(senza_consegna)} non consegnano niente.\n\n")
        f.write("## Le corsie accese\n\n")
        f.write("| corsia | orologio | scrive | consegna |\n|---|---|---|---|\n")
        for r in sorted(acc, key=lambda x: x["corsia"]):
            o = "; ".join(r["orologio"]) if r["orologio"] else "**nessuno**"
            f.write(f"| `{r['corsia']}` | {o} | {', '.join('`'+x+'`' for x in r['scrive'][:4]) or '—'} "
                    f"| {r['consegna']} |\n")
        if doppi:
            f.write("\n## Scritti da più di una corsia (qui nascono le sovrascritture)\n\n")
            for p, c in sorted(doppi.items()):
                f.write(f"- `{p}` ← {', '.join('`'+x+'`' for x in sorted(c))}\n")
    print(f"\nMAPPA | scritti {USCITA_MD} e {USCITA_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
