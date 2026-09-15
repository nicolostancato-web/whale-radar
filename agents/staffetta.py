#!/usr/bin/env python3
"""
STAFFETTA — il passaggio di consegne fra un risveglio e il successivo.

L'IDEA NON E' NOSTRA (09/09, presa da un video su un agente che fa trading con soldi veri). La frase
che vale: **la continuita' viene dai registri condivisi, non dall'AI che ricorda la conversazione**.
Ogni risveglio e' apolide: se non trova scritto cosa e' successo e QUAL E' IL PROSSIMO LAVORO, ricomincia
a orientarsi da zero — e orientarsi da zero, ogni volta, costa piu' del lavoro.

Non e' un altro rapporto da leggere. E' l'UNICO foglio da leggere per primo: dice in che stato siamo,
cosa e' cambiato, e cosa va fatto adesso — in una riga, non in un paragrafo.

Sola lettura sui dati, nessuna chiamata a pagamento. €0.
"""
import calendar, glob, gzip, json, os, re, time, urllib.request

REPO = "nicolostancato-web/whale-radar"
TOK = os.environ.get("WR_PAT") or os.environ.get("GITHUB_TOKEN", "")
now = int(time.time())
CORSIE = {"motore": "engine ", "ricerca": "ricerca ", "loop 0": "loop0 ", "sperimenti": "sperimenti "}


def commits():
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/commits?per_page=100",
                                     headers={"Accept": "application/vnd.github+json",
                                              **({"Authorization": f"token {TOK}"} if TOK else {})})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except Exception:
        return []


def verdetto(file):
    """La riga di verdetto di un esperimento, senza rileggersi tutto il rapporto."""
    if not os.path.exists(file): return None
    try:
        t = open(file).read()
    except Exception: return None
    m = re.search(r"^> ([✅❌⏸️].{0,180})", t, re.M)
    return m.group(1).strip() if m else None


def coda():
    p = "data/coda_esperimenti.json"
    if not os.path.exists(p): return [], []
    try:
        d = json.load(open(p))["esperimenti"]
    except Exception: return [], []
    return ([e for e in d if e.get("stato", "").startswith("IN CORSO")],
            [e for e in d if e.get("stato") == "APERTO"])


def accumulo():
    """I NUMERI DELL'ACCUMULO, E LA LORO VARIAZIONE. Un contatore fermo su un numero grande sembra
    salute: se non si vede QUANTO E' CAMBIATO dall'ultima volta, 'fermo' e 'pieno' hanno lo stesso
    aspetto. Qui accanto a ogni numero c'e' il suo delta, e un delta zero e' un allarme, non un dato."""
    ora = {}
    for ch in ("base", "solana", "robinhood"):
        serie = {os.path.basename(f).replace(".jsonl.gz", "")
                 for f in glob.glob(f"data/multichain/{ch}/candles/*.gz")}
        battito = {os.path.basename(f).replace(".jsonl.gz", "")
                   for f in glob.glob(f"data/multichain/{ch}/pulse/*.gz")}
        scambi = {os.path.basename(f).replace(".jsonl.gz", "")
                  for f in glob.glob(f"data/multichain/{ch}/trades/*.gz")}
        ora[f"{ch}/candele"] = len(serie)
        ora[f"{ch}/battito"] = len(battito)
        # IL NUMERO CHE DECIDE SE POSSIAMO FARE LE DOMANDE CHE CONTANO (14/09). Un token ci serve
        # davvero solo se abbiamo INSIEME il suo prezzo e i suoi scambi: senza scambi non sappiamo
        # CHI compra, in che ordine, con che tempi — ed e' li' che l'audit dice che vive il segnale.
        # I primi scambi evaporano (la fonte gratuita tiene solo gli ultimi ~300), quindi questo
        # numero si puo' costruire solo IN AVANTI. Se non sale, non stiamo andando da nessuna parte.
        completi = (serie | battito) & scambi
        ora[f"{ch}/COMPLETI (prezzo+scambi)"] = len(completi)
        # MA COMPLETI NON BASTA (14/09). Avere il file degli scambi non vuol dire avere gli scambi
        # GIUSTI: la fonte gratuita conserva solo gli ultimi ~300, quindi se interroghiamo un token
        # gia' maturo i primi acquisti sono spariti. E sono proprio quelli a dire CHI e' entrato per
        # primo, in che ordine, con che tempi — l'unica cosa che l'audit indica come possibile sede
        # del segnale. Qui si stima su un campione quanti file arrivano DAVVERO prima dell'entrata:
        # e' il numero che decide se il 3 ottobre avremo qualcosa su cui fare la domanda vera.
        try:
            campione = sorted(completi)[:150]
            buoni = 0; letti = 0
            for a in campione:
                sf = f"data/multichain/{ch}/candles/{a}.jsonl.gz"
                if not os.path.exists(sf): sf = f"data/multichain/{ch}/pulse/{a}.jsonl.gz"
                tf = f"data/multichain/{ch}/trades/{a}.jsonl.gz"
                try:
                    with gzip.open(sf, "rt") as fo:
                        pts = [json.loads(l).get("ts") for l in fo if l.strip()][:400]
                    with gzip.open(tf, "rt") as fo:
                        tr = [json.loads(l) for l in fo if l.strip()][:600]
                except Exception:
                    continue
                pts = [x for x in pts if x]
                if not pts or not tr: continue
                letti += 1
                # IL CRITERIO GIUSTO, NON QUELLO COMODO (14/09). La prima versione chiedeva solo che
                # il primo scambio arrivasse abbastanza presto: passava il 99%. Ma per sapere CHI
                # compra e in che ordine non basta che gli scambi comincino presto — devono essere
                # ABBASTANZA prima del momento in cui compreremmo. Con la richiesta vera (almeno 6
                # scambi e 3 acquisti prima dell'entrata) si passa dal 99% al 18%.
                # Una misura che dice 99 dove la verita' e' 18 e' peggio di nessuna misura: quella
                # tace, questa rassicura.
                lim = min(pts) + 3 * 3600 - 3 * 3600      # entrata a +3h, meno il ritardo osservativo
                pre = [x for x in tr if (x.get("ts") or 0) <= lim]
                if len(pre) >= 6 and sum(1 for x in pre if x.get("kind") == "buy") >= 3: buoni += 1
            # UNO ZERO NON PUO' NASCERE DA UN ERRORE (14/09). La prima versione ha scritto "0%" su
            # tutte e tre le chain mentre in locale erano 29 su 29: mancava l'import di gzip, ogni
            # lettura moriva, l'except la ingoiava e il contatore restava a zero. Uno zero che viene
            # da un guasto e uno zero che viene dal mondo sono indistinguibili a chi legge — ed e'
            # il difetto che sto inseguendo da giorni, qui dentro il pezzo che doveva sorvegliarlo.
            # Adesso si riporta una percentuale SOLO se qualcosa e' stato davvero letto.
            if letti >= 10:
                ora[f"{ch}/DOMANDABILI (stima %)"] = round(buoni / letti * 100)
            else:
                ora[f"{ch}/utilizzabili"] = -1      # -1 = non misurabile, non "zero"
        except Exception:
            pass
    try:
        ck = json.load(open("data/whale_candles_checkpoint.json"))
        vals = [v for v in ck.values() if isinstance(v, (int, float))]
        ora["robinhood/toccati 12h"] = sum(1 for v in vals if v > now - 12 * 3600)
    except Exception:
        pass
    st = "data/staffetta_storico.json"
    try:
        prima = json.load(open(st))
    except Exception:
        prima = {}
    delta = {k: ora[k] - prima.get("valori", {}).get(k, ora[k]) for k in ora}
    quando = prima.get("ts")
    try:
        json.dump({"ts": now, "valori": ora}, open(st, "w"))
    except Exception:
        pass
    return ora, delta, ((now - quando) / 60 if quando else None)


def astra():
    """DA QUANTO NON PARLA IL CONSULENTE. E' un anello della catena come le corsie: Claude costruisce,
    i loop misurano, lui dice cosa costruire. Se tace, la catena e' rotta a monte e tutto il resto
    continua a girare benissimo verso la direzione sbagliata.
    RIMESSA IL 13/09: era sparita perche' avevo ripubblicato questo file da una cartella locale
    vecchia. L'eta' si legge DENTRO il rapporto: la data di modifica la azzera un clone."""
    f = "ASTRA_REVIEW.md"
    if not os.path.exists(f): return None
    try:
        testa = open(f).read(400)
    except Exception: return None
    m = re.search(r"\*(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC", testa)
    if not m: return None
    try:
        tt = time.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M")
        return (now - calendar.timegm(tt)) / 3600
    except Exception:
        return None


def main():
    cs = commits()
    vive, mute = [], []
    for nome, pref in CORSIE.items():
        for c in cs:
            m = c["commit"]["message"].split("\n")[0]
            if m.startswith(pref):
                import calendar
                tt = time.strptime(c["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")
                min_fa = (now - calendar.timegm(tt)) / 60
                (vive if min_fa < 90 else mute).append(f"{nome} ({min_fa:.0f}′)")
                break
        else:
            if cs: mute.append(f"{nome} (nessun commit)")

    incorso, aperti = coda()
    esp = [("liquidità impegnata", "LIQUIDITA_IMPEGNATA.md"),
           ("costo d'uscita", "COSTO_USCITA.md"),
           ("fuori dal recinto", "SPERIMENTALE.md")]

    L = ["# 🏃 STAFFETTA — leggi QUESTO per primo",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · aggiornato da solo a ogni giro*", "",
         "> La continuità viene dai **registri condivisi**, non dal ricordarsi la conversazione. Chi si",
         "> sveglia adesso non ha memoria: qui trova dove siamo e **qual è il prossimo lavoro**.", "",
         "## Le corsie", ""]
    L += [f"- 🟢 vive: {', '.join(vive) if vive else '—'}"]
    if mute: L += [f"- 🔴 **mute: {', '.join(mute)}** ← prima di ogni altra cosa, capire perché"]
    L += ["", "## Gli esperimenti vivi", ""]
    for nome, f in esp:
        v = verdetto(f)
        L.append(f"- **{nome}**: {v if v else '_nessun verdetto scritto_'}")
    # L'ACCUMULO, con il delta accanto
    ora_v, delta, min_fa = accumulo()
    ore_astra = astra()
    astra_rotta = ore_astra is None or ore_astra > 26
    L += ["", "## Il consulente esterno", ""]
    if ore_astra is None:
        L += ["- 🔴 **Il consulente non ha mai parlato**, o il suo rapporto non è leggibile."]
    elif astra_rotta:
        L += [f"- 🔴 **Tace da {ore_astra:.0f} ore** (dovrebbe parlare due volte al giorno).",
              "  Se tace, la catena è rotta a monte: tutto il resto continua a girare benissimo",
              "  verso la direzione sbagliata."]
    else:
        L += [f"- 🟢 Ha parlato **{ore_astra:.0f} ore fa**."]
    L += ["", "## Stiamo accumulando?", ""]
    if min_fa:
        L += [f"*Variazione rispetto a **{min_fa:.0f} minuti fa**.*", ""]
    L += ["| cosa | quanti | cambiato di |", "|---|---|---|"]
    fermi = []
    for k in sorted(ora_v):
        d = delta.get(k, 0)
        segno = f"**+{d}**" if d > 0 else ("—" if d == 0 else str(d))
        if d == 0 and min_fa and min_fa > 25: fermi.append(k)
        L.append(f"| {k} | {ora_v[k]:,} | {segno} |")
    L += [""]
    if fermi:
        L += [f"> 🔴 **Fermi da {min_fa:.0f} minuti**: {', '.join(fermi)}. Un contatore che non cambia",
              "> non è un contatore alto: è lavoro che non sta succedendo.", ""]
    L += ["", f"In coda e non ancora aperti: **{len(aperti)}** "
              f"({', '.join(str(e['n']) for e in aperti) if aperti else 'nessuno'}).", ""]

    # IL PROSSIMO LAVORO, ESPLICITO. Una riga sola: se ce ne fossero cinque non sarebbe il prossimo.
    if mute:
        prossimo = f"Riaccendere e capire perché tace: **{mute[0]}**. Una corsia muta blocca tutto il resto."
    elif astra_rotta:
        prossimo = ("**Far parlare il consulente**: tace, e nessuno ci sta dicendo cosa costruire. "
                    "Costruire nella direzione sbagliata costa più che non costruire.")
    elif fermi:
        prossimo = (f"**L'accumulo è fermo su {fermi[0]}**: le corsie girano ma non entra niente. "
                    "Prima di qualsiasi idea nuova, capire perché — un esperimento su dati che non "
                    "crescono misura sempre la stessa cosa.")
    elif not aperti and not incorso:
        prossimo = ("**Riempire la coda.** Nessun esperimento aperto: la macchina gira e non ha niente da "
                    "bruciare, ed è lo spreco peggiore che possiamo fare.")
    elif any("⏸" in (verdetto(f) or "") for _, f in esp):
        prossimo = ("Lasciare accumulare i **giorni indipendenti** agli esperimenti in ⏸️ e intanto aprire "
                    f"il prossimo della coda (ne restano {len(aperti)}). Non si conclude prima dei 15 giorni.")
    else:
        prossimo = f"Aprire il prossimo esperimento della coda (ne restano {len(aperti)}) e scriverne il criterio di morte PRIMA."
    L += ["## ➡️ Il prossimo lavoro", "", f"> {prossimo}", "",
          "> **Perché una riga sola**: se il prossimo lavoro fossero cinque cose, non sarebbe il",
          "> prossimo — sarebbe un elenco, e un elenco non fa partire nessuno."]
    L += ["", "---", "",
          "> ⚠️ **Questo foglio va letto da GitHub, non da una copia locale.** Gli errori peggiori di",
          "> lettura dello stato sono venuti tutti da lì: una cartella scaricata ieri mostra numeri di",
          "> ieri e sembrano di oggi. Qui sotto c'è la data del calcolo, e se non è di pochi minuti fa",
          "> il foglio non vale.", "",
          f"*Calcolato alle **{time.strftime('%H:%M UTC', time.gmtime(now))}** del "
          f"{time.strftime('%d/%m/%Y', time.gmtime(now))}.*"]
    # IL DIARIO: una riga per ogni giro in cui e' cambiato qualcosa (11/09, richiesta di Nicolo).
    # Serve a una cosa precisa: aprire il file e VEDERE che le macchine hanno lavorato. Uno stato
    # fotografato non lo dice — dice solo com'e' adesso, e "adesso" somiglia a "sempre uguale".
    # Un diario racconta il MOVIMENTO, ed e' l'unica prova leggibile che qualcosa e' successo mentre
    # nessuno guardava. Le righe uguali alla precedente non si scrivono: un diario che ripete non si
    # legge piu', e allora smette di servire.
    # ANCHE I CALI (13/09). Il diario mostrava solo le crescite: un archivio che si SVUOTA era
    # invisibile. Oggi ho passato mezz'ora a temere che qualcosa stesse cancellando le candele di
    # Base — era la potatura, legittima e documentata — ma il diario non lo diceva ne' in un senso
    # ne' nell'altro. Un registro che racconta solo le buone notizie non e' un registro.
    cambi = [f"{k} +{delta[k]}" for k in sorted(delta) if delta.get(k, 0) > 0]
    cali = [f"{k} {delta[k]}" for k in sorted(delta) if delta.get(k, 0) < 0]
    if cali: cambi = cali + cambi
    riga = None
    if cambi:
        riga = (f"- **{time.strftime('%d/%m %H:%M UTC', time.gmtime(now))}** — accumulo: "
                + ", ".join(cambi[:6]))
    elif ore_astra is not None and ore_astra < 1:
        riga = f"- **{time.strftime('%d/%m %H:%M UTC', time.gmtime(now))}** — il consulente ha parlato"
    if riga:
        try:
            vecchie = open("DIARIO.md").read().splitlines() if os.path.exists("DIARIO.md") else []
        except Exception:
            vecchie = []
        testa = ["# 📓 DIARIO — cosa è successo, giro per giro", "",
                 "> Le macchine lavorano anche quando nessuno guarda. Qui resta la traccia: una riga",
                 "> per ogni giro in cui **è cambiato qualcosa**. I giri identici al precedente non si",
                 "> scrivono — un diario che ripete smette di essere letto, e allora smette di servire.", ""]
        corpo = [r for r in vecchie if r.startswith("- **")]
        if not corpo or corpo[0] != riga:
            corpo = [riga] + corpo
        try:
            open("DIARIO.md", "w").write("\n".join(testa + corpo[:300]))
        except Exception:
            pass

    open("STAFFETTA.md", "w").write("\n".join(L))
    print(f"STAFFETTA | vive:{len(vive)} mute:{len(mute)} aperti:{len(aperti)}", flush=True)


if __name__ == "__main__":
    main()
