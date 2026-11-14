"""I GUASTI DELLE CORSIE, riportati a me invece che nella casella di Nicolo'.

== PERCHE' ESISTE (7/10/2026) ==

Le email di GitHub sui giri falliti arrivavano a Nicolo', che non puo' farci niente e non vuole
vederle: «stoppa tutte le email che mi arrivano cosi... tutte, non ne voglio piu' vedere 1. pero'
tu devi assicurarti che sai questi errori».

Spegnere l'avviso senza prendersi il carico sarebbe la cosa peggiore: un sistema che non avvisa
nessuno e' peggio di uno che avvisa la persona sbagliata. Quindi l'iscrizione ai repo e' spenta
(API, verificata) e questo agente gira a OGNI giro del mio loop, dentro `dal_di_fuori.sh`.

== LA DISTINZIONE CHE CONTA ==

Non tutti i guasti sono nostri. Il 7/10 cinque corsie sono fallite tutte insieme con HTTP 500 sul
rilancio: GitHub Actions era in **major outage** dichiarato. Un guasto di GitHub non si ripara, si
aspetta; uno nostro si ripara. Confondere i due porta a «aggiustare» codice sano, che e' il modo
piu' veloce di rompere qualcosa che funziona.

Quindi ogni guasto viene etichettato: `GITHUB` (fuori dal nostro controllo, dichiarato dal loro
stato) oppure `NOSTRO` (da guardare). E lo stato di cio' che ho gia' visto sta su file, perche'
fra un giro e l'altro passano minuti e un guasto non visto non deve sparire.
"""
import datetime
import json
import os
import re
import sys
import urllib.request

REPO = os.environ.get("REPO", "nicolostancato-web/whale-radar")
STATO = os.environ.get("STATO_GUASTI", "/tmp/guasti_visti.json")
CRED = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")


def _tok():
    return re.search(r"ghp_[A-Za-z0-9]+", open(CRED).read()).group(0)


def _g(u, tok):
    r = urllib.request.Request(u, headers={"Authorization": f"token {tok}",
                                           "Accept": "application/vnd.github+json"})
    return json.load(urllib.request.urlopen(r, timeout=40))


def actions_in_avaria():
    """GitHub sta dichiarando un guasto su Actions? (None se non si riesce a chiedere.)"""
    try:
        d = json.load(urllib.request.urlopen(
            "https://www.githubstatus.com/api/v2/components.json", timeout=25))
        for c in d["components"]:
            if c["name"] == "Actions":
                return c["status"] != "operational", c["status"]
    except Exception:
        pass
    return None, "non leggibile"


def main():
    tok = _tok()
    visti = set()
    if os.path.exists(STATO):
        try:
            visti = set(json.load(open(STATO)).get("run", []))
        except Exception:
            pass
    # SOLO I GUASTI RECENTI, E IL RESTO CONTATO (7/10). La prima versione chiedeva gli ultimi
    # 30 falliti senza data: il repo ne ha centinaia dal 28 settembre, quindi a ogni giro
    # riportava trenta guasti vecchi e il rapporto diventava rumore — e un rapporto che e'
    # rumore non si legge, cioe' torna a non sapere niente. Le corsie di allora in gran parte
    # non esistono piu'.
    da = (datetime.datetime.now(datetime.timezone.utc)
          - datetime.timedelta(hours=int(os.environ.get("ORE", "36")))).strftime("%Y-%m-%d")
    try:
        giri = _g(f"https://api.github.com/repos/{REPO}/actions/runs"
                  f"?status=failure&per_page=50&created=%3E%3D{da}", tok)["workflow_runs"]
    except Exception as e:
        print(f"GUASTI | non riesco a chiedere a GitHub ({str(e)[:50]}): "
              f"NON dico che va tutto bene, dico che non lo so.")
        return 0
    nuovi = [r for r in giri if str(r["id"]) not in visti]
    print(f"GUASTI | guardo dal {da} in poi ({len(giri)} falliti nel periodo, "
          f"{len(nuovi)} che non avevo ancora visto)")
    avaria, stato_gh = actions_in_avaria()
    if not nuovi:
        print(f"GUASTI | nessun guasto nuovo (Actions: {stato_gh})")
        return 0

    print(f"GUASTI | {len(nuovi)} giri falliti da quando ho guardato (Actions: {stato_gh})")
    nostri = 0
    for r in nuovi[:12]:
        passi, job_tutti_ok = [], None
        try:
            jobs = _g(f"https://api.github.com/repos/{REPO}/actions/runs/{r['id']}/jobs",
                      tok)["jobs"]
            for j in jobs:
                for st in j["steps"]:
                    if st["conclusion"] == "failure":
                        passi.append(f"{j['name']}/{st['name']}")
            # UN GIRO FALLITO CON TUTTI I JOB RIUSCITI NON E' UN NOSTRO DIFETTO (7/10): e'
            # successo alla corsia `vivo`, due job su due riusciti e il giro segnato come
            # fallito. Vuol dire che qualcosa non e' partito lato GitHub. Dirlo e' piu' utile
            # che dire «non so», e meno falso che dire «colpa nostra».
            job_tutti_ok = bool(jobs) and all(j["conclusion"] == "success" for j in jobs)
        except Exception:
            passi = []
        # IL RIARMO CHE NON PARTE DURANTE UN GUASTO DI GITHUB NON E' UN NOSTRO DIFETTO.
        # Il 7/10 cinque corsie sono fallite cosi' mentre Actions era in major outage.
        solo_riarmo = bool(passi) and all("riarm" in p.lower() for p in passi)
        if not passi and job_tutti_ok:
            etichetta = "INFRASTRUTTURA (tutti i job riusciti, il giro segnato fallito)"
        elif not passi:
            # NESSUN PASSO FALLITO LEGGIBILE NON VUOL DIRE «COLPA NOSTRA» (7/10). La prima
            # versione, un'ora di vita, etichettava «NOSTRO — da guardare» due giri di cui non
            # sapeva niente: prove assenti trasformate in un'accusa. E' la stessa famiglia
            # dell'errore che mi perseguita, girata al contrario — prima un'assenza diventava
            # un'assoluzione, qui diventava una condanna. Un'assenza resta un'assenza.
            etichetta = ("NON SO (nessun passo leggibile; Actions in avaria: probabile GitHub)"
                         if avaria else "NON SO (nessun passo fallito leggibile)")
            if not avaria:
                nostri += 1
        elif avaria and solo_riarmo:
            etichetta = "GITHUB (avaria dichiarata, il lavoro era riuscito)"
        elif solo_riarmo:
            etichetta = "RIARMO (il lavoro e' riuscito, non e' ripartita)"
            nostri += 1
        else:
            etichetta = "NOSTRO — da guardare"
            nostri += 1
        print(f"   {r['name'][:34]:34} {r['created_at'][5:16]}Z  {etichetta}")
        for p in passi[:3]:
            print(f"      passo fallito: {p}")
    json.dump({"run": sorted(visti | {str(r["id"]) for r in nuovi})}, open(STATO, "w"))
    if nostri == 0:
        print("GUASTI | nessuno di questi e' colpa nostra: non tocco niente.")
    else:
        print(f"GUASTI | {nostri} da guardare io, non Nicolo'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
