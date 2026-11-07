"""Quali corsie GitHub non riesce a leggere. Lo chiede a GitHub, non lo indovina.

PERCHE' ESISTE (2/10). Due volte in un giorno un file di corsia illeggibile ha mandato email a
raffica: `riserve` con un lavoro senza passi, e `guardia` con codice Python a colonna zero dentro
`run: |` — in YAML quelle righe chiudono il blocco. In entrambi i casi la corsia FALLISCE a ogni
suonata, e in un'ora sono nove email.

IL SINTOMO E' ESATTO E VIENE DA GITHUB: quando non riesce a leggere il file, come `name` della
corsia riporta il PERCORSO (`.github/workflows/guardia.yml`) invece del nome dichiarato dentro.
Non c'e' niente da interpretare.

PERCHE' NON PROVO A LEGGERE LO YAML DA SOLO. Ci ho provato mezz'ora fa: un controllo che
guardava l'indentazione dei blocchi segnalava SEI file sani (i commenti a colonna zero sono
legali) e NON vedeva quello rotto. Reimplementare il lettore di qualcun altro produce un
controllo che sbaglia in entrambe le direzioni — il tipo peggiore, perche' blocca il lavoro buono
e lascia passare quello rotto.
**Quando l'autorita' sa la risposta, si chiede a lei.**
"""
import json
import os
import sys
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "nicolostancato-web/whale-radar")


def illeggibili(tok):
    r = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/workflows?per_page=100",
        headers={"Authorization": "token " + tok, "Accept": "application/vnd.github+json"})
    d = json.load(urllib.request.urlopen(r, timeout=60))
    fuori = []
    for w in d.get("workflows", []):
        nome, percorso = w.get("name", ""), w.get("path", "")
        # GitHub mette il percorso come nome solo quando non ha saputo leggere il file
        if nome.endswith(".yml") or nome == percorso:
            fuori.append((percorso, w.get("state")))
    return fuori


if __name__ == "__main__":
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        print("CORSIA ILLEGGIBILE | senza token non posso controllare. Questa guardia e' CIECA, "
              "non tranquilla.", flush=True)
        sys.exit(0)
    try:
        fuori = illeggibili(tok)
    except Exception as e:
        print(f"CORSIA ILLEGGIBILE | non riesco a chiedere a GitHub ({type(e).__name__}): "
              f"guardia cieca, non tranquilla.", flush=True)
        sys.exit(0)
    for p, stato in fuori:
        print(f"   ILLEGGIBILE  {p} (stato: {stato}) — GitHub non sa leggerla e la corsia "
              f"FALLISCE a ogni suonata, una email per volta", flush=True)
    if fuori:
        print(f"CORSIA ILLEGGIBILE | {len(fuori)} corsie illeggibili: vanno riparate o spente "
              f"SUBITO, perche' ognuna manda una email a ogni suonata.", flush=True)
        sys.exit(1)
    print("CORSIA ILLEGGIBILE | GitHub legge tutte le corsie", flush=True)
