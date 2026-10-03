"""Chi non gira da troppo tempo viene rilanciato. Usato da PIU' guardiani, non da uno.

IL SORVEGLIANTE CHE TACE (30/09). Ho scritto una guardia per accorgermi delle corsie ferme, e
mezz'ora dopo ho scoperto che LEI STESSA era ferma da quasi cinque ore. La domanda «chi
sorveglia il sorvegliante» non si risolve con un guardiano piu' in alto — sarebbe la stessa
domanda un piano sopra, e prima o poi anche quello tace.

Si risolve con una RETE: questa funzione vive in un file solo e la chiamano guardiani diversi,
che si tengono d'occhio a vicenda. Basta che UNO sia vivo perche' gli altri tornino, e la
probabilita' che tacciano tutti insieme e' il prodotto delle singole, non la somma.

E sta qui, in un posto solo, per una seconda ragione imparata lo stesso giorno: quando ho
riscritto a memoria un calcolo di date gia' corretto altrove, ho rifatto lo stesso errore di
fuso. **Una lezione scritta in un file non protegge il file accanto.**
"""
import datetime as dt
import json
import os
import urllib.request

# corsia -> dopo quanti minuti di silenzio la si considera ferma
CRITICHE = {
    # DEDOTTE DALL'OROLOGIO (2/10): il limite di silenzio e' tre volte l'intervallo
    # dichiarato nel cron. Quattordici corsie avevano l'orologio, nessun riarmo e
    # NESSUNO che le guardasse: togliendo i riarmi che dormivano ho reso questa lista
    # l'unico motore di riserva, e ne guardava dodici su ventisei.
    "accumulator": 360,
    "astra": 600,
    "censimento": 90,
    "ciclo": 360,
    "collector": 360,
    "deposito": 180,
    "finanziatori": 60,
    "guardiani": 240,
    "heartbeat": 180,
    "hook": 90,
    "iniziatori": 180,
    "insider": 180,
    "insieme": 180,
    "ispezione": 180,
    "paper_bot": 360,
    "piu_intelligente": 4320,
    "popolazione": 180,
    "previsioni": 120,
    "prova_avanti": 4320,
    "pubblicatore": 60,
    "riparazione": 180,
    "riserve": 180,
    "scoperta": 90,
    "sentinella": 120,
    "soccorso": 90,
    "solana_helius": 90,
    "storico": 180,
    "vivo": 120,
}


def consulente_muto():
    """Da quante ore tace il consulente esterno. E' un anello della catena come le corsie.

    IL 30/09 NICOLO' HA CHIESTO «perche' Astra non viene chiamato da giorni?» e la risposta e'
    stata: nessuna corsia lo esegue, veniva lanciato A MANO. Il sistema lo sapeva — `staffetta.py`
    scriveva in rosso «tace da 155 ore» — ma quel rapporto lo leggeva nessuno, me compreso.
    Un allarme che nessuno legge non e' un allarme: e' un archivio di rimpianti.
    Qui la riga finisce dentro l'uscita della sentinella, che si guarda.

    NON chiama Astra: costa $0,17 a consulenza e la decisione sul ritmo e' di Nicolo'.
    """
    for f in ("ASTRA_REVIEW.md", "../ASTRA_REVIEW.md"):
        if os.path.exists(f):
            eta = (dt.datetime.now().timestamp() - os.path.getmtime(f)) / 3600
            # l'eta' del file mente dopo un clone: si legge la data DENTRO il rapporto
            try:
                import re
                testo = open(f, encoding="utf-8", errors="replace").read(400)
                m = re.search(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})", testo)
                if m:
                    q = dt.datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M")
                    eta = (dt.datetime.utcnow() - q).total_seconds() / 3600
            except Exception:
                pass
            if eta > 26:
                return [f"IL CONSULENTE ESTERNO TACE DA {eta:.0f} ORE. Nessuna corsia lo esegue: "
                        f"va lanciato a mano, e il ritmo lo decide Nicolo' ($0,17 a consulenza)."]
            return []
    return ["IL CONSULENTE ESTERNO: non trovo nemmeno il suo ultimo rapporto."]


def _api(url, tok, posta=False):
    r = urllib.request.Request(
        url, data=b'{"ref":"main"}' if posta else None,
        method="POST" if posta else "GET",
        headers={"Authorization": "token " + tok, "Accept": "application/vnd.github+json"})
    return urllib.request.urlopen(r, timeout=20)


def decisioni_violate():
    """Le decisioni permanenti che non sono piu' rispettate. Arriva dove qualcuno guarda."""
    import subprocess
    import sys as _s
    qui = os.path.dirname(os.path.abspath(__file__))
    try:
        r = subprocess.run([_s.executable, "-B", os.path.join(qui, "decisioni.py")],
                           capture_output=True, text=True, timeout=180)
    except Exception as e:
        return [f"non riesco a controllare le decisioni ({type(e).__name__})"]
    return [x.strip() for x in r.stdout.splitlines() if x.strip().startswith(("GRAVE", "AVVISO"))]


def inventario_rotto():
    """Corsie attese che non ci sono piu', o che tacciono oltre il loro limite.

    IL GUASTO CHE QUESTO CHIUDE (1/10, consiglio di Grok): GitHub non avvisa quando un workflow
    viene cancellato o disabilitato, e una corsia che non parte non produce nessun esito da
    segnalare. Per un mese 33 corsie su 60 sono state ferme senza che nulla gridasse.
    L'elenco atteso vive FUORI dal repository (sul computer di Nicolo'), perche' se vivesse
    dentro potrei cancellare insieme la corsia e la prova che dovesse esistere.
    """
    import subprocess
    import sys as _s
    qui = os.path.dirname(os.path.abspath(__file__))
    try:
        r = subprocess.run([_s.executable, "-B", os.path.join(qui, "inventario.py")],
                           capture_output=True, text=True, timeout=300)
    except Exception as e:
        return [f"non riesco a controllare l'inventario ({type(e).__name__})"]
    return [x.strip() for x in r.stdout.splitlines() if "PROBLEMA" in x][:8]


def tutto(quali=None):
    """Le corsie ferme PIU' il consulente muto: una riga sola da stampare."""
    return (ferme_e_rilanciate(quali) + consulente_muto() + decisioni_violate()
            + inventario_rotto())


MEMORIA_RILANCI = "data/rilanci.json"


def _rilanci():
    try:
        return json.load(open(MEMORIA_RILANCI))
    except (OSError, ValueError):
        return {}


def _segna_rilancio(corsia, quando):
    d = _rilanci()
    d[corsia] = quando
    try:
        os.makedirs(os.path.dirname(MEMORIA_RILANCI), exist_ok=True)
        json.dump(d, open(MEMORIA_RILANCI, "w"), indent=1, sort_keys=True)
    except OSError:
        pass


def ferme_e_rilanciate(quali=None):
    """
    LA TEMPESTA DI RILANCI, COSTRUITA DA ME STANOTTE (1/10). Grok la chiama `retry storm`.
    `scoperta` ha avuto QUATTRO cancellazioni in otto minuti: due guardiani girano insieme,
    entrambi la vedono ferma, entrambi la rilanciano — e ogni nuovo giro uccide quello in volo,
    che risulta fermo, e viene rilanciato di nuovo. Il rimedio diventa la malattia.
    Qui ogni corsia non si rilancia piu' di una volta per finestra: la memoria dei rilanci sta
    su disco, condivisa fra i guardiani, non nella testa di ognuno.
    """
    """Torna le righe da stampare. Rilancia da sola: accorgersene e basta e' meta' del lavoro."""
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        # NON SI TACE QUANDO NON SI PUO' GUARDARE (30/09). Prima qui si tornava una lista vuota,
        # che chi chiama legge come «nessuna corsia ferma»: la guardia diceva «tutto bene»
        # proprio perche' era cieca. E' il difetto che questo progetto incontra piu' spesso.
        return ["NON POSSO CONTROLLARE LE CORSIE FERME: manca GH_TOKEN. "
                "Questa guardia e' cieca, non tranquilla."]
    repo = os.environ.get("GITHUB_REPOSITORY", "nicolostancato-web/whale-radar")
    fuori = []
    for corsia, limite in (quali or CRITICHE).items():
        try:
            giri = json.load(_api(
                f"https://api.github.com/repos/{repo}/actions/workflows/{corsia}.yml/runs?per_page=10",
                tok)).get("workflow_runs", [])
            # NON SI RILANCIA CHI HA GIA' UN GIRO IN CODA (1/10). Qui si guardava solo il giro
            # PIU' RECENTE: se quello era gia' stato annullato mentre un altro era ancora in
            # coda, la corsia sembrava muta e si rilanciava lo stesso. Con tre guardie
            # indipendenti (questa, `guardiani`, l'osservatore sul Mac) il risultato era un giro
            # ogni due minuti — 11:53, 11:55, 11:57 — nessuno dei quali faceva in tempo a
            # partire su venti macchine condivise. Misurato il 1/10: `hook` fermo da 342 minuti
            # con OTTO giri di fila annullati, nessuno fallito.
            # Una corsia che aspetta un posto non e' una corsia ferma: rilanciarla la allontana.
            if not giri or any(g["status"] != "completed" for g in giri):
                continue
            # NON SI RILANCIA CHI FALLISCE SEMPRE PER LO STESSO MOTIVO (1/10).
            # `astra` fallisce perche' manca la chiave fra i segreti: un guasto DETERMINISTICO.
            # La rete la vedeva muta, la rilanciava, fallendo di nuovo — e Nicolo' riceveva una
            # email a ogni giro. E' lo stesso errore delle tre ore di ritentativi del 30/09, in
            # forma nuova: ritentare ha senso solo se la causa puo' essere cambiata nel frattempo.
            esiti = [g.get("conclusion") for g in giri if g.get("conclusion")]
            if len(esiti) >= 2 and all(e == "failure" for e in esiti[:2]):
                fuori.append(f"{corsia}: fallisce sempre ({len(esiti)} volte di fila). "
                             f"NON la rilancio: serve una mano, non un altro tentativo.")
                continue
            # L'ORA DI GITHUB E' UTC E VA LETTA COME UTC: `time.mktime` la leggerebbe come locale
            # e `time.timezone` non tiene conto dell'ora legale. Errore gia' fatto due volte.
            # L'ETA' SI CONTA DALL'ULTIMO SUCCESSO, NON DALL'ULTIMO LANCIO (1/10). Si prendeva
            # giri[0], il piu' recente qualunque fosse l'esito: tre annullamenti di fila — che
            # non fanno nulla — rimettevano l'orologio a zero, e la guardia diceva «nei limiti»
            # su `hook`, morta da sei ore. Un lancio non e' un lavoro.
            # IL LAVORO, NON IL VERDETTO DEL GIRO (1/10). Si guardava `conclusion == success`
            # del GIRO. Ma un giro viene marcato «annullato» anche quando le sue raccolte sono
            # andate benissimo e si e' fermato solo il passo di RIARMO, che aspetta dieci minuti
            # e viene superato dal giro successivo. Misurato oggi: `hook` e `censimento` avevano
            # ZERO giri «riusciti» e QUATTRO giri in cui il lavoro era riuscito. Le dichiaravo
            # morte, la sentinella suonava, tre guardie le rilanciavano — e stavano bene.
            # IN POSITIVO: una corsia e' viva se i suoi lavori VERI sono riusciti; il riarmo che
            # si fa annullare non conta, perche' non e' il lavoro.
            vivi = [g for g in giri if _ha_lavorato(g, tok)]
            # nessun successo fra i giri guardati: si usa il piu' vecchio che si vede, cosi'
            # l'eta' e' almeno quella — e la corsia passa dalla stessa porta di rilancio di
            # tutte le altre, invece che da una scorciatoia tutta sua
            riferimento = vivi[0] if vivi else giri[-1]
            nato = dt.datetime.strptime(riferimento["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=dt.timezone.utc)
            minuti = (dt.datetime.now(dt.timezone.utc) - nato).total_seconds() / 60
            if minuti < limite:
                continue
            # UNA VOLTA PER FINESTRA, NON UNA PER GUARDIANO
            ultimo = _rilanci().get(corsia, 0)
            if (dt.datetime.now(dt.timezone.utc).timestamp() - ultimo) / 60 < limite:
                continue
            try:
                _api(f"https://api.github.com/repos/{repo}/actions/workflows/{corsia}.yml/dispatches",
                     tok, posta=True)
                _segna_rilancio(corsia, dt.datetime.now(dt.timezone.utc).timestamp())
                fuori.append(f"{corsia}: ferma da {minuti:.0f} min (limite {limite}) — RILANCIATA")
            except Exception as e:
                fuori.append(f"{corsia}: ferma da {minuti:.0f} min e NON sono riuscito a "
                             f"rilanciarla ({type(e).__name__})")
        except Exception:
            continue
    return fuori
