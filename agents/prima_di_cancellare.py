"""Si rifiuta di cancellare una copia di lavoro se contiene qualcosa che non e' su GitHub.

PERCHE' ESISTE (1/10, paura di Nicolo' e aveva ragione).

Nicolo': «ho paura che appunto cancelli della roba importante».

L'1/10 ho cancellato una copia di lavoro da 26 GB per liberare il disco. Prima l'ho fatto bene:
un invio di verifica, dodici file in sospeso, tutti gia' su GitHub. Ma quella era la MIA
disciplina — e la disciplina e' esattamente la cosa che stanotte ha fallito tre volte.

Qui diventa un meccanismo: si confronta ogni file della copia con quello su GitHub, e se qualcosa
e' diverso o assente **la cancellazione si rifiuta**. Non avvisa: si rifiuta.

Il 25/09 era andata perduta una giornata di lavoro proprio cosi' — file scritti in locale, mai
pubblicati, spariti con una pulizia del disco. Quella volta ho riparato il caso. Questa la classe.
"""
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "nicolostancato-web/whale-radar")
# cio' che non deve bloccare: roba generata, copie di comodo, cartelle di servizio
IGNORA = (".git/", "__pycache__/", ".DS_Store", "FASCICOLO_ASTRA.txt",
          "data/autorizzazione.json", "data/decisioni_stato.json",
          "data/requisiti_stato.json", "data/rilanci.json", "data/ripristino_provato.json")


def _su_github(percorso, tok):
    """L'impronta git del file su GitHub, o None se non c'e'."""
    url = f"https://api.github.com/repos/{REPO}/contents/{percorso}"
    try:
        r = urllib.request.Request(url, headers={"Authorization": "token " + tok})
        return json.load(urllib.request.urlopen(r, timeout=30)).get("sha")
    except Exception:
        return None


def _impronta_git(percorso):
    """L'impronta che git darebbe a questo file: cosi' si confronta con quella di GitHub."""
    dati = open(percorso, "rb").read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(dati))
    h.update(dati)
    return h.hexdigest()


def main():
    cartella = sys.argv[1] if len(sys.argv) > 1 else "."
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        print("   NON POSSO CONTROLLARE senza token: la cancellazione si RIFIUTA. "
              "Non sapere non e' sapere che va bene.", flush=True)
        sys.exit(1)
    os.chdir(cartella)
    # i file che git considera nuovi o modificati: sono i soli che possono essere perduti
    sospetti = []
    try:
        out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                             timeout=120).stdout
    except Exception as e:
        print(f"   NON POSSO CONTROLLARE ({type(e).__name__}): la cancellazione si RIFIUTA.",
              flush=True)
        sys.exit(1)
    for riga in out.splitlines():
        stato, nome = riga[:2], riga[3:].strip().strip('"')
        if stato.strip() == "D" or not nome:
            continue
        if any(nome.startswith(x) or nome.endswith(x) for x in IGNORA):
            continue
        if not os.path.isfile(nome):
            continue
        sospetti.append(nome)

    perduti = []
    for nome in sospetti:
        sha_remoto = _su_github(nome, tok)
        if sha_remoto is None:
            perduti.append((nome, "non esiste su GitHub"))
        elif sha_remoto != _impronta_git(nome):
            perduti.append((nome, "diverso da quello su GitHub"))

    print(f"PRIMA DI CANCELLARE | {len(sospetti)} file da verificare, {len(perduti)} a rischio",
          flush=True)
    for nome, perche in perduti:
        print(f"   NON PUBBLICATO  {nome}: {perche}", flush=True)
    if perduti:
        print("   LA CANCELLAZIONE SI RIFIUTA. Pubblica prima, poi cancella.", flush=True)
        sys.exit(1)
    print("   tutto cio' che c'e' qui esiste anche su GitHub: si puo' cancellare.", flush=True)


if __name__ == "__main__":
    main()
