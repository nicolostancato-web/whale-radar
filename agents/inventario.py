"""Confronta le corsie che DOVREBBERO esistere con quelle che esistono davvero.

IL GUASTO CHE QUESTO CHIUDE (1/10, consiglio di Grok).

Per un mese 33 corsie su 60 non hanno girato e nessuno se n'e' accorto. Il motivo e' strutturale,
non una distrazione: **GitHub non avvisa quando un workflow viene cancellato o disabilitato**, e
una corsia che non parte non produce nessun esito da segnalare. L'email-on-failure non puo'
prendere questo guasto, perche' non c'e' nessun fallimento.

Grok: «il controllo e': lista attesa, scritta in un posto dove il bot non scrive, confrontata
con GET /actions/workflows e con l'ultimo run andato a buon fine».

LA PARTE CHE CONTA E' «DOVE IL BOT NON SCRIVE». Se l'elenco atteso vive nel repository, io posso
cancellare insieme la corsia E la prova che dovesse esistere — ed e' esattamente come e' sparito
`compliance_check.py`. Quindi l'autorita' e' un file sul computer di Nicolo':

    ~/Documents/whale-radar-inventario-atteso.json

La copia nel repository serve alla corsia, ma se le due divergono **vince quella locale** e si
grida. GitHub Actions non puo' scrivere sul Mac di Nicolo': e' un dominio di guasto diverso,
che e' il punto.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

LOCALE = os.path.expanduser("~/Documents/whale-radar-inventario-atteso.json")
NEL_REPO = "data/inventario_atteso.json"
REPO = os.environ.get("GITHUB_REPOSITORY", "nicolostancato-web/whale-radar")


def _perche(giri, tok):
    """Perche' questa corsia non riesce: tempo scaduto, o mai partita.

    Si distingue da un fatto solo e non opinabile: se il lavoro ha un `started_at`, e' PARTITO
    e non ha fatto in tempo. Se non lo ha, non e' mai partito: e' stato superato in coda.
    """
    import urllib.request
    partiti = fermi = 0
    for g in giri[:4]:
        if g.get("conclusion") not in ("cancelled", "failure"):
            continue
        try:
            r = urllib.request.Request(g["jobs_url"],
                                       headers={"Authorization": "token " + tok,
                                                "Accept": "application/vnd.github+json"})
            lavori = json.load(urllib.request.urlopen(r, timeout=30)).get("jobs", [])
        except Exception:
            continue
        for x in lavori:
            if x.get("conclusion") != "cancelled":
                continue
            if x.get("started_at"):
                partiti += 1
            else:
                fermi += 1
    if partiti and not fermi:
        return "TEMPO SCADUTO: il lavoro parte e non fa in tempo. Serve piu' tempo, o un budget dentro il programma"
    if fermi and not partiti:
        return "MAI PARTITA: superata in coda. Serve lanciarla MENO, non di piu'"
    if partiti and fermi:
        return f"meta' e meta': {partiti} lavori scaduti, {fermi} mai partiti"
    return None


def _ha_lavorato(giro, tok):
    """Vero se i lavori veri di questo giro sono riusciti, riarmo escluso.

    Se i lavori non si riescono a leggere si torna al verdetto del giro: meglio il criterio
    vecchio e imperfetto che un elenco che si zittisce perche' una chiamata non e' andata.
    """
    if giro.get("conclusion") == "success":
        return True
    if giro.get("conclusion") is None:
        return False
    try:
        import urllib.request
        r = urllib.request.Request(giro["jobs_url"],
                                   headers={"Authorization": "token " + tok,
                                            "Accept": "application/vnd.github+json"})
        lavori = json.load(urllib.request.urlopen(r, timeout=30)).get("jobs", [])
    except Exception:
        return False
    veri = [x for x in lavori if "riarmo" not in x["name"].lower()]
    return bool(veri) and all(x.get("conclusion") == "success" for x in veri)


def _api(percorso, tok):
    r = urllib.request.Request(f"https://api.github.com/repos/{REPO}{percorso}",
                               headers={"Authorization": "token " + tok,
                                        "Accept": "application/vnd.github+json"})
    return json.load(urllib.request.urlopen(r, timeout=30))


def atteso():
    """L'elenco atteso. Vince quello locale, se c'e': il bot non lo puo' toccare."""
    for percorso, chi in ((LOCALE, "il computer di Nicolo'"), (NEL_REPO, "il repository")):
        try:
            d = json.load(open(percorso))
            return d, chi
        except (OSError, ValueError):
            continue
    return None, None


def main():
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        print("INVENTARIO | senza token non posso guardare: NON dico che va tutto bene.",
              flush=True)
        sys.exit(1)
    att, chi = atteso()
    if att is None:
        print(f"INVENTARIO | non esiste nessun elenco atteso. Lo scrivo da quello che c'e' "
              f"ADESSO, e da domani un confronto avra' senso.", flush=True)
        att = {"generato": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "corsie": {}}
        chi = "generato adesso"

    vive = {}
    for w in _api("/actions/workflows?per_page=100", tok)["workflows"]:
        nome = w["path"].split("/")[-1][:-4]
        vive[nome] = {"stato": w["state"]}
        try:
            giri = _api(f"/actions/workflows/{w['id']}/runs?per_page=10", tok)["workflow_runs"]
        except Exception:
            giri = []
        # IL LAVORO, NON IL VERDETTO DEL GIRO (1/10). Si contava solo `conclusion == success`.
        # Ma un giro risulta «annullato» anche quando le sue raccolte sono riuscite e si e'
        # fermato soltanto il passo di RIARMO, che aspetta dieci minuti e viene superato dal
        # giro dopo. Misurato oggi: `hook` e `censimento` avevano ZERO giri «riusciti» e QUATTRO
        # giri in cui il lavoro era riuscito. Questo elenco le dava per mute, la sentinella
        # suonava, tre guardie le rilanciavano — e stavano bene. Un allarme falso su due e' il
        # modo piu' rapido di far ignorare quello vero.
        # IN POSITIVO: il successo di una corsia sono i suoi lavori VERI riusciti; il riarmo
        # che si fa annullare non e' il lavoro.
        ok = [g for g in giri if _ha_lavorato(g, tok)]
        vive[nome]["ultimo_successo"] = ok[0]["created_at"] if ok else None
        vive[nome]["perche_non_riesce"] = _perche(giri, tok) if not ok else None

    if not att["corsie"]:
        # L'ELENCO DEVE SAPERE COM'E' FATTO IL SISTEMA (1/10). La prima versione metteva 24 ore
        # di silenzio massimo a TUTTE le corsie: ma venti sono a riposo per scelta — orologio
        # spento, codice intatto — e sarebbero andate in allarme tutte, cioe' l'allarme sarebbe
        # diventato rumore e nessuno l'avrebbe piu' letto.
        # Il limite si legge dal file della corsia: chi non ha orologio non deve girare.
        import glob as _g
        import re as _re
        att["corsie"] = {}
        for n_, v_ in vive.items():
            f_ = f".github/workflows/{n_}.yml"
            testo = ""
            try:
                testo = open(f_, encoding="utf-8", errors="replace").read()
            except OSError:
                pass
            a_riposo = "A RIPOSO" in testo or "- cron:" not in testo
            if a_riposo:
                att["corsie"][n_] = {"stato_atteso": v_["stato"],
                                     "ore_massime_di_silenzio": None,
                                     "nota": "a riposo o manuale: non deve girare da sola"}
                continue
            # dall'orologio si ricava ogni quanto DICE di voler girare, e si concede il triplo
            m_ = _re.search(r'- cron: "(\S+) (\S+)', testo)
            ore = 3
            if m_ and m_.group(2) != "*":
                try:
                    ore = int(m_.group(2).replace("*/", "")) * 3
                except ValueError:
                    ore = 9
            att["corsie"][n_] = {"stato_atteso": v_["stato"],
                                 "ore_massime_di_silenzio": max(3, min(72, ore))}
        os.makedirs(os.path.dirname(NEL_REPO), exist_ok=True)
        json.dump(att, open(NEL_REPO, "w"), indent=1, sort_keys=True)
        print(f"   scritto {NEL_REPO} con {len(att['corsie'])} corsie. "
              f"COPIALO IN {LOCALE}: li' io non posso toccarlo, ed e' il punto.", flush=True)
        return

    guai = []
    for nome, c in sorted(att["corsie"].items()):
        v = vive.get(nome)
        if v is None:
            guai.append(f"{nome}: ATTESA ma NON ESISTE PIU'. GitHub non avvisa di questo.")
            continue
        if v["stato"] != "active":
            # DISATTIVATA E' UNA DECISIONE, NON UN GUASTO (1/10). La prima versione dava un
            # limite di silenzio anche a chi era `disabled_manually`: due allarmi su sei erano
            # suoi errori di taratura, e un allarme sbagliato su tre e' il modo piu' rapido di
            # far ignorare gli altri.
            if c.get("stato_atteso") == "active":
                guai.append(f"{nome}: attesa attiva, e' «{v['stato']}» — se e' voluto, "
                            f"aggiorna l'elenco atteso")
            continue
        if c.get("ore_massime_di_silenzio") is None:
            continue            # a riposo per scelta: il silenzio e' il suo stato giusto
        q = v["ultimo_successo"]
        if q is None:
            # DUE CAUSE OPPOSTE SOTTO LA STESSA PAROLA (1/10). «Annullato» puo' voler dire
            # «tempo scaduto» (il lavoro e' partito e non ha fatto in tempo) oppure «superato
            # in coda» (non e' mai partito). Il rimedio e' l'OPPOSTO: nel primo caso serve piu'
            # tempo, nel secondo serve lanciare MENO. Per tre tick ho applicato il secondo
            # rimedio al primo problema, rilanciando corsie che morivano di fretta.
            perche = v.get("perche_non_riesce")
            guai.append(f"{nome}: nessun giro riuscito negli ultimi dieci"
                        + (f" — {perche}" if perche else ""))
            continue
        ore = (dt.datetime.now(dt.timezone.utc)
               - dt.datetime.strptime(q, "%Y-%m-%dT%H:%M:%SZ").replace(
                   tzinfo=dt.timezone.utc)).total_seconds() / 3600
        limite = c.get("ore_massime_di_silenzio", 24)
        if ore > limite:
            guai.append(f"{nome}: ultimo successo {ore:.0f} ore fa (massimo {limite})")

    nuove = sorted(set(vive) - set(att["corsie"]))
    print(f"INVENTARIO | elenco atteso da {chi}: {len(att['corsie'])} corsie. "
          f"Reali: {len(vive)}. Problemi: {len(guai)}. Nuove non dichiarate: {len(nuove)}",
          flush=True)
    for g in guai:
        print(f"   PROBLEMA  {g}", flush=True)
    for n in nuove:
        print(f"   nuova     {n}: esiste e non e' nell'elenco atteso", flush=True)
    if guai:
        sys.exit(1)


if __name__ == "__main__":
    main()
