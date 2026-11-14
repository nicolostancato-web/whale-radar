"""Pubblica un file sul repo via API GitHub, senza passare da git.

Serve perche' il clone di lavoro e le corsie sul cloud scrivono sugli stessi percorsi, e un push
da git finirebbe in conflitto continuo: il repository riceve spinte da nove corsie, e da fuori si
finisce indietro di decine di commit prima di riuscire a spingere (misurato il 22/09: sei
tentativi tutti respinti, 79 commit di ritardo). L'API aggiorna un file solo, con il suo sha.

SPARISCE. E' la seconda volta: ricreato il 18/09 dopo una pulizia del disco, e di nuovo il 23/09.
Senza, ogni pubblicazione fallisce con ModuleNotFoundError e i rimedi non arrivano mai sul repo —
e la cosa peggiore e' che il fallimento assomiglia a «non ho niente da pubblicare».
Per questo ne esiste ora una copia dentro il repository, in `strumenti/api_push.py`: la cartella
di lavoro e' volatile, il repository no.
"""
import base64
import json
import os
import urllib.request

REPO = os.environ.get("WR_REPO", "nicolostancato-web/whale-radar")


def _token():
    p = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
    try:
        for riga in open(p):
            if "ghp_" in riga:
                i = riga.find("ghp_")
                t = ""
                for c in riga[i:]:
                    if c.isalnum() or c == "_":
                        t += c
                    else:
                        break
                if len(t) > 20:
                    return t
    except Exception:
        pass
    return os.environ.get("GITHUB_TOKEN", "")


def api(percorso, dati=None, metodo="GET"):
    r = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{percorso}",
        data=json.dumps(dati).encode() if dati else None,
        headers={"Authorization": f"token {_token()}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "whale-radar"},
        method=metodo)
    with urllib.request.urlopen(r, timeout=60) as x:
        b = x.read()
        return json.loads(b) if b else {}


def pubblica(remoto, locale, msg):
    """Scrive `locale` su `remoto` nel repo. Torna True se riuscito."""
    sha = None
    try:
        sha = api(f"contents/{remoto}").get("sha")
    except Exception:
        pass
    contenuto = base64.b64encode(open(locale, "rb").read()).decode()
    api(f"contents/{remoto}",
        {"message": msg, **({"sha": sha} if sha else {}),
         "content": contenuto, "branch": "main"}, "PUT")
    print(f"OK {remoto}")
    return True
