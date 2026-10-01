"""Scarica l'insieme se c'e' ed e' fresco; lo costruisce solo se manca o e' vecchio.

PERCHE' ESISTE (1/10). Tre corsie — `insieme`, `ciclo`, `prova_avanti` — ricostruivano lo STESSO
dato, e la costruzione dura circa 75 minuti per chain. Su venti macchine condivise sono tre ore
e mezza di lavoro identico, ripetuto, che toglie posto a tutto il resto: Grok lo chiama
`resource starvation`.

Le avevo rese autosufficienti di proposito, e per un buon motivo: il giudice della prova in
avanti leggeva un file che nessuno aggiornava, e sarebbe rimasto a zero per sempre. Dipendere da
qualcun altro e' come muoiono le cose in questo sistema.

Il compromesso: si PROVA a scaricare, e si costruisce solo se manca o se ha piu' di ORE_MASSIME.
Autosufficienti quando serve, parsimoniose quando non serve.
"""
import os
import subprocess
import sys
import time
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "nicolostancato-web/whale-radar")
ORE_MASSIME = float(os.environ.get("ORE_MASSIME", 8))


def scarica(chain, suffisso):
    nome = f"insieme_{chain}{suffisso}.jsonl.gz"
    p = f"data/loop1/{nome}"
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        return False, "senza token non posso scaricare"
    os.makedirs("data/loop1", exist_ok=True)
    try:
        r = urllib.request.Request(
            f"https://api.github.com/repos/{REPO}/contents/{p}",
            headers={"Authorization": "token " + tok,
                     "Accept": "application/vnd.github.v3.raw"})
        dati = urllib.request.urlopen(r, timeout=300).read()
    except Exception as e:
        return False, f"non scaricabile ({type(e).__name__})"
    if len(dati) < 10000 or dati[:2] != b"\x1f\x8b":
        # UN FILE TROPPO PICCOLO O NON COMPRESSO E' UN MESSAGGIO D'ERRORE TRAVESTITO (1/10):
        # mi e' gia' successo di salvare un JSON di errore col nome di un archivio.
        return False, f"il file scaricato non e' un archivio ({len(dati)} byte)"
    open(p, "wb").write(dati)
    return True, f"scaricato, {len(dati)/1e6:.1f} MB"


def abbastanza_fresco(chain, suffisso):
    p = f"data/loop1/insieme_{chain}{suffisso}.jsonl.gz"
    if not os.path.exists(p):
        return False
    ore = (time.time() - os.path.getmtime(p)) / 3600
    return ore <= ORE_MASSIME


def main():
    suffisso = os.environ.get("SUFFISSO", "")
    suffisso = f"_{suffisso}" if suffisso and not suffisso.startswith("_") else suffisso
    for chain in ("robinhood", "base"):
        ok, perche = scarica(chain, suffisso)
        if ok and abbastanza_fresco(chain, suffisso):
            print(f"PRENDI | {chain}{suffisso}: {perche} — non lo ricostruisco", flush=True)
            continue
        print(f"PRENDI | {chain}{suffisso}: {perche if not ok else 'troppo vecchio'} — "
              f"lo costruisco", flush=True)
        amb = dict(os.environ, CHAIN=chain)
        r = subprocess.run([sys.executable, "-B", os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "insieme.py")], env=amb, timeout=9000)
        if r.returncode != 0:
            print(f"   {chain}: COSTRUZIONE FALLITA", flush=True)


if __name__ == "__main__":
    main()
