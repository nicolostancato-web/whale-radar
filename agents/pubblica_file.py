"""Pubblica i file cambiati passando dall'interfaccia di GitHub, non da git.

PERCHE' (28/09). La copia di lavoro e' SUPERFICIALE (`--depth 1`): serve, perche' l'intera storia
pesa gigabyte e il disco del Mac si era riempito. Ma con una copia superficiale git non puo'
dimostrare la parentela fra i commit, e il server rifiuta il push dicendo «sei indietro» **anche
quando sei allineato**. Non e' contesa: e' un limite strutturale, e nessun numero di tentativi lo
supera. Ne ho fatti dieci, poi altri dieci, prima di capirlo.

**Si smette di combattere con lo strumento sbagliato.** Qui si mandano i FILE, uno per uno, con
l'interfaccia che GitHub offre apposta: niente storia, niente parentele, niente push. Se qualcuno
scrive lo stesso file nel frattempo, il server risponde «conflitto», si rilegge la sua versione e si
riprova — che e' il comportamento giusto, non un ripiego.

Vale per i file di CODICE e di TESTO che scrivo io. I dati continuano a viaggiare con git dalle
corsie, dove le copie sono complete e il push funziona.
"""
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = "nicolostancato-web/whale-radar"
CRED = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")


def _token():
    for l in open(CRED, encoding="utf-8", errors="ignore"):
        m = re.search(r"(gh[ps]_[A-Za-z0-9]+)", l)
        if m:
            return m.group(1)
    return None


def _api(url, metodo="GET", dati=None, tok=None):
    r = urllib.request.Request(
        url, method=metodo, data=json.dumps(dati).encode() if dati else None,
        headers={"Authorization": f"token {tok}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(r, timeout=60) as f:
            b = f.read()
            return json.loads(b) if b else {}, None
    except urllib.error.HTTPError as e:
        return None, e


def manda(percorso, messaggio, tok):
    """Un file. Torna True se e' arrivato."""
    url = f"https://api.github.com/repos/{REPO}/contents/{percorso}"
    contenuto = base64.b64encode(open(percorso, "rb").read()).decode()
    for tentativo in range(1, 6):
        attuale, _ = _api(url, tok=tok)
        dati = {"message": messaggio, "content": contenuto}
        if attuale and attuale.get("sha"):
            if attuale.get("content", "").replace("\n", "") == contenuto:
                # IL SILENZIO PIU' COSTOSO (29/09). Un file identico a quello gia' pubblicato
                # significa quasi sempre che la correzione NON E' ENTRATA: la sostituzione non
                # ha combaciato e non ha protestato. Prima qui si tornava True zitti, e la
                # pubblicazione sembrava riuscita. Tre strategie sono morte cosi'.
                print(f"   {percorso}: INVARIATO — identico a quello su GitHub. "
                      f"Se ti aspettavi un cambiamento, la tua modifica NON e' entrata.",
                      flush=True)
                return True
            dati["sha"] = attuale["sha"]
        _, err = _api(url, "PUT", dati, tok)
        if err is None:
            return True
        if err.code == 409:                      # qualcuno ha scritto nel frattempo: si rilegge
            time.sleep(1 + tentativo)
            continue
        print(f"   {percorso}: RIFIUTATO ({err.code}) {err.read()[:120]}", flush=True)
        return False
    print(f"   {percorso}: conflitto ripetuto, non mandato", flush=True)
    return False


def _registra(file, messaggio):
    """Un registro di CIO' CHE ABBIAMO PRODOTTO, che sopravvive alla compattazione della storia.

    PERCHE' (29/09). La domanda quotidiana raccoglieva le prove da `git log`. Ma il compattatore
    riscrive la storia ogni giorno, e dopo quel momento il lavoro prodotto compare solo dentro il
    suo commit gigante — che il filtro scarta come manutenzione, giustamente.
    Risultato misurato oggi: tre verdetti pubblicati nelle ultime 24 ore, e le prove dicevano
    «verdetti: zero, ipotesi: zero» — da cui il giudizio «attivita' alta e intelligenza ferma».
    **Una misura cieca non produce un giudizio prudente: ne produce uno sbagliato e severo.**

    Stessa lezione del timbro dell'insieme: **il contenuto sopravvive, la storia viene potata.**
    Quindi cio' che conta si scrive in un file, non si deduce dai commit.
    """
    import time as _t
    p = "data/prodotti.json"
    try:
        tutti = json.load(open(p)) if os.path.exists(p) else []
    except Exception:
        tutti = []
    tutti.append({"quando": int(_t.time()), "messaggio": messaggio, "file": file})
    tutti = tutti[-500:]                      # bastano gli ultimi: non e' un archivio
    os.makedirs("data", exist_ok=True)
    json.dump(tutti, open(p, "w"), indent=1, ensure_ascii=False)


def main():
    messaggio = sys.argv[1] if len(sys.argv) > 1 else "aggiornamento"
    tok = _token()
    if not tok:
        print("PUBBLICA | manca il token di GitHub nel file delle credenziali")
        return 1
    cambiati = [l.split()[-1] for l in subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()]
    cambiati = [f for f in cambiati if os.path.isfile(f)]
    if not cambiati:
        print("PUBBLICA | niente da mandare")
        return 0
    ok = 0
    mandati = []
    for f in cambiati:
        if manda(f, messaggio, tok):
            ok += 1
            mandati.append(f)
            print(f"   {f}: mandato", flush=True)
    _registra(mandati, messaggio)
    print(f"PUBBLICA | {ok} file su {len(cambiati)} sono su GitHub", flush=True)
    return 0 if ok == len(cambiati) else 1


if __name__ == "__main__":
    raise SystemExit(main())
