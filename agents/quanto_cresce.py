"""Quanti byte grossi sono stati scritti, in una finestra dichiarata in UTC.

PERCHE' ESISTE (10/10, due errori miei nello stesso pomeriggio).
1) Avevo stimato la crescita contando le riscritture dei file grossi nei commit: gonfiata quattro
   volte, perche' i commit di FUSIONE rielencano un file senza cambiarlo e git un contenuto
   identico lo conserva una volta sola. Qui le fusioni si saltano.
2) Poi ho creduto di aver sbagliato un numero GIUSTO (53 MB in 30 minuti) e l'ho ritirato,
   perche' confrontavo a mente orari UTC di GitHub con l'ora locale del Mac. Ritirare un numero
   vero e' peggio che pubblicarne uno falso: insegna a non fidarsi di quelli veri.

LA REGOLA, in positivo: la finestra si calcola in UTC esplicito, e si dichiara se la pagina dei
commit si e' riempita — perche' una pagina piena vuol dire che la finestra e' piu' larga di
quella chiesta, e il numero vale come minimo, non come misura.
"""
import collections
import datetime
import json
import os
import re
import sys
import urllib.request

REPO = "nicolostancato-web/whale-radar"
SOGLIA = 1_000_000


def _tok():
    for v in ("WR_PAT", "GITHUB_TOKEN"):
        if os.environ.get(v):
            return os.environ[v]
    c = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
    m = re.search(r"ghp_[A-Za-z0-9]+", open(c, encoding="utf-8", errors="ignore").read())
    return m.group(0) if m else None


def _api(u, tok):
    r = urllib.request.Request(u, headers={"Authorization": f"token {tok}"})
    return json.load(urllib.request.urlopen(r, timeout=90))


def misura(minuti=30):
    tok = _tok()
    if not tok:
        print("CRESCITA | senza token non posso guardare: NON dico che va tutto bene")
        return None
    dim = {x["path"]: x.get("size", 0)
           for x in _api(f"https://api.github.com/repos/{REPO}/git/trees/main?recursive=1",
                         tok)["tree"] if x["type"] == "blob"}
    ora = datetime.datetime.now(datetime.timezone.utc)
    da = (ora - datetime.timedelta(minutes=minuti)).strftime("%Y-%m-%dT%H:%M:%SZ")
    cm, p = [], 1
    piena = False
    while p <= 4:
        b = _api(f"https://api.github.com/repos/{REPO}/commits?per_page=100&page={p}&since={da}",
                 tok)
        cm += b
        if len(b) < 100:
            break
        p += 1
        piena = True
    byte = collections.Counter()
    for c in cm:
        d = _api(f"https://api.github.com/repos/{REPO}/commits/{c['sha']}", tok)
        if len(d.get("parents", [])) > 1:
            continue                      # fusione: nessun contenuto nuovo
        for f in d.get("files", []):
            if dim.get(f["filename"], 0) > SOGLIA:
                byte[f["filename"]] += dim[f["filename"]]
    tot = sum(byte.values())
    print(f"CRESCITA | da {da} (UTC, {minuti} min): {len(cm)} commit, "
          f"{tot/1e6:.0f} MB di file grossi riscritti = {tot/1e6*1440/minuti/1000:.2f} GB/giorno"
          + ("  [pagine piene: e' un MINIMO]" if piena else ""))
    for f, n in byte.most_common(5):
        print(f"   {n/1e6:7.1f} MB  {f}")
    return tot


if __name__ == "__main__":
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    sys.exit(0 if misura(m) is not None else 1)
