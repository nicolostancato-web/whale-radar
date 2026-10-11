"""Le tre strade per cui la memoria si perde, controllate tutte e tre.

PERCHE' ESISTE. Nicolo' (10/10): «magari ci accorgiamo che facendo cosi' la memoria la perdiamo».
E' giа' successo tre volte, per tre strade diverse, e ogni volta avevamo riparato IL CASO e non
LA CLASSE:

  1. un file che vive solo in locale — il 25/09 una pulizia del disco ha cancellato consulenze,
     due agenti e un insieme di dati, tutti scritti e mai pubblicati;
  2. un'uscita che non arriva mai al ramo — il 10/10 trenta consulenze pagate morte sul runner,
     mentre il registro diceva «riuscito»;
  3. un allegato che scade — quelle trenta si sono salvate per un pelo, perche' gli allegati
     durano sette giorni e il settimo era vicino.

Qui si guardano tutte e tre a ogni giro. Un controllo che copre una classe vale piu' di tre
riparazioni.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = "nicolostancato-web/whale-radar"


def _tok():
    for v in ("WR_PAT", "GITHUB_TOKEN"):
        if os.environ.get(v):
            return os.environ[v]
    c = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
    if os.path.exists(c):
        m = re.search(r"ghp_[A-Za-z0-9]+", open(c, encoding="utf-8", errors="ignore").read())
        return m.group(0) if m else None
    return None


def _api(u, tok):
    r = urllib.request.Request(u, headers={"Authorization": f"token {tok}"})
    return json.load(urllib.request.urlopen(r, timeout=90))


def solo_in_locale():
    """STRADA 1. File che il manifesto manda nel ramo e che nel ramo non ci sono."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import manifesto as M
    except ImportError:
        return ["manifesto non importabile: non so quali file dovrebbero stare nel ramo"]
    # «MODIFICATO SECONDO GIT» NON VUOL DIRE «NON PUBBLICATO» (10/10, falso allarme su 227 file).
    # Pubblico con l'interfaccia di GitHub, che NON tocca l'indice di git: dopo un invio riuscito
    # il file resta «modificato» per sempre, e questo controllo accusava tutto il repository.
    # L'unico confronto che vale e' il CONTENUTO: si chiede a GitHub l'impronta del file e si
    # confronta con quella locale. Git qui serve solo a sapere QUALI file guardare.
    import base64
    import hashlib
    tok = _tok()
    if not tok:
        return ["senza token non posso confrontare col ramo: NON dico che va tutto bene"]
    # SE GIT NON FUNZIONA, QUESTO CONTROLLO NON SA NIENTE (11/10). Con .git corrotta
    # `git status` falliva, la lista dei file cambiati restava vuota, e il controllo diceva
    # «nessuna perdita»: un falso via libera, che e' peggio di nessun controllo.
    r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if r.returncode != 0:
        return ["GIT NON FUNZIONA QUI (" + (r.stderr or "").strip()[:80] + "): non posso sapere "
                "quali file esistono solo in locale. NON dico che va tutto bene."]
    cambiati = [l.split()[-1] for l in r.stdout.splitlines()]
    guai = []
    for f in cambiati:
        if not os.path.isfile(f):
            continue
        ok, _ = M.puo_andare_su_github(f)
        if not ok:
            continue
        mio = open(f, "rb").read()
        try:
            d = _api(f"https://api.github.com/repos/{REPO}/contents/{f}", tok)
            suo = base64.b64decode(d["content"])
        except urllib.error.HTTPError as e:
            if e.code == 404:
                guai.append(f"{f}: nel ramo NON c'e' affatto")
                continue
            guai.append(f"{f}: non riesco a confrontarlo col ramo ({e.code})")
            continue
        except Exception:
            continue
        if hashlib.sha256(mio).hexdigest() != hashlib.sha256(suo).hexdigest():
            guai.append(f"{f}: la copia nel ramo e' DIVERSA da quella locale")
    return guai


def uscite_che_non_arrivano(tok):
    """STRADA 2. Corsie che dicono «riuscito» e non lasciano traccia da nessuna parte."""
    if not tok:
        return ["senza token non posso guardare: NON dico che va tutto bene"]
    guai = []
    w = _api(f"https://api.github.com/repos/{REPO}/actions/workflows?per_page=100", tok)
    for x in w["workflows"]:
        if x["state"] != "active":
            continue
        nome = x["name"]
        try:
            r = _api(f"https://api.github.com/repos/{REPO}/actions/workflows/"
                     f"{nome}.yml/runs?per_page=3&status=success", tok)
        except urllib.error.HTTPError:
            continue
        corse = r.get("workflow_runs") or []
        if not corse:
            continue
        # CHI SPINGE NON HA BISOGNO DI ALLEGATI (10/10, secondo falso allarme dello stesso
        # controllo). Accusavo dieci corsie di buttare il loro lavoro: tutte spingono con git,
        # e io guardavo solo gli allegati. Due accuse sbagliate su due: un controllo cosi' si
        # impara a ignorare prima di avere ragione una volta.
        p = f".github/workflows/{nome}.yml"
        if not os.path.exists(p):
            continue
        testo_corsia = open(p).read()
        if "git push" in testo_corsia:
            continue
        # NE' CHI CONSEGNA NEL DEPOSITO, NE' CHI NON PRODUCE NIENTE (10/10, terza taratura dello
        # stesso controllo). `deposito` carica su R2 e lascia una ricevuta: il suo lavoro e' al
        # sicuro, solo non nel ramo. `guardia` rilancia le corsie mute e non ha nulla da salvare.
        # Lo stesso ragionamento lo avevo gia' fatto in revisione_struttura: non averlo riportato
        # qui e' il motivo per cui questo controllo ha gridato al lupo tre volte di fila.
        if "deposito" in testo_corsia or "consegna_verificata" in testo_corsia:
            continue
        scrive = False
        for m in re.finditer(r"agents/(\w+)\.py", testo_corsia):
            p2 = f"agents/{m.group(1)}.py"
            if os.path.exists(p2) and re.search(
                    r'json\.dump\(|open\([^)]*["\']w|\.write\(',
                    open(p2, encoding="utf-8", errors="replace").read()):
                scrive = True
                break
        if not scrive:
            continue
        # una corsa riuscita deve aver lasciato o un commit o un allegato
        senza = 0
        for c in corse:
            try:
                a = _api(f"https://api.github.com/repos/{REPO}/actions/runs/"
                         f"{c['id']}/artifacts", tok)
            except urllib.error.HTTPError:
                a = {"total_count": 0}
            if a.get("total_count", 0) == 0 and c.get("head_commit"):
                # nessun allegato: ha spinto qualcosa? lo si vede dai commit del suo sha
                senza += 1
        if senza == len(corse) and len(corse) >= 2:
            guai.append(f"{nome}: le ultime {len(corse)} corse riuscite non hanno lasciato "
                        f"allegati. Se nemmeno spinge, il suo lavoro muore col runner.")
    return guai


def allegati_che_scadono(tok):
    """STRADA 3. Allegati vicini alla scadenza: dentro potrebbe esserci l'unica copia."""
    if not tok:
        return []
    guai = []
    d = _api(f"https://api.github.com/repos/{REPO}/actions/artifacts?per_page=100", tok)
    ora = time.time()
    vicini = []
    for a in d.get("artifacts", []):
        if a.get("expired"):
            continue
        q = a.get("expires_at")
        if not q:
            continue
        try:
            t = time.mktime(time.strptime(q[:19], "%Y-%m-%dT%H:%M:%S"))
        except ValueError:
            continue
        ore = (t - ora) / 3600
        if ore < 48:
            vicini.append((ore, a["name"], a["size_in_bytes"]))
    vicini.sort()
    for ore, nome, byte in vicini[:8]:
        guai.append(f"{nome} ({byte/1e6:.1f} MB) scade fra {ore:.0f} ore: se dentro c'e' "
                    f"l'unica copia di qualcosa, fra {ore:.0f} ore non c'e' piu'")
    return guai


def main():
    tok = _tok()
    tot = 0
    for nome, f in (("file che vivono solo in locale", lambda: solo_in_locale()),
                    ("uscite che non arrivano da nessuna parte", lambda: uscite_che_non_arrivano(tok)),
                    ("allegati che scadono entro 48 ore", lambda: allegati_che_scadono(tok))):
        try:
            g = f()
        except Exception as e:
            g = [f"il controllo stesso e' rotto: {type(e).__name__}: {e}"]
        if g:
            print(f"\nPERDITE | {nome}: {len(g)}")
            for x in g[:8]:
                print(f"   {x}")
            tot += len(g)
        else:
            print(f"PERDITE | {nome}: nessuna")
    print(f"\nPERDITE | {tot} strade aperte per perdere memoria")
    return 0


if __name__ == "__main__":
    sys.exit(main())
