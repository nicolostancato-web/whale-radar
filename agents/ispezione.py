#!/usr/bin/env python3
"""
ISPEZIONE — il **LOOP 0**. Gira sempre, non si ferma mai, e controlla che tutti gli altri lavorino.

I TRE LOOP (nomenclatura ufficiale, direttiva Nicolò 31/08):
  · **LOOP 0 — ISPEZIONE**  : che ogni componente del team faccia il suo lavoro. UNO solo, ma con verdetto
                              separato per chain. Non si spegne mai: se domani entra un agente nuovo nel
                              team, dev'esserci ancora qualcuno che controlla anche lui.
  · **LOOP 1 — PERCENTUALE**: alzare la percentuale. Esiste in OGNI chain, con logiche diverse.
  · **LOOP 2 — DEMO LIVE**  : il conto verso €3.000. Esiste in ogni chain, oggi tutti fermi dal cancello.

Perche' il LOOP 0 vale piu' della lavagna: dieci dipendenti dove uno fuma, uno va al bar e uno inventa
numeri possono anche mostrare percentuali alte oggi — fra sei mesi non avranno niente. Un team dove ognuno
ha un compito preciso puo' partire da zero e superarli, perche' la soluzione salta fuori dal numero di test
fatti bene. L'organizzazione viene prima del risultato: il risultato e' una conseguenza.

L'investitore entra nella stanza e interroga OGNI componente del team.

Nasce il 31/08 da un problema reale: ogni volta che Nicolò chiedeva "controlla che tutto vada bene" saltava
fuori un guasto diverso — un verbale fermo da 4 ore, un cron saltato, un timeout scaduto. Non perché il
sistema fosse rotto, ma perché **nessuno controllava i controllori in modo sistematico**: lo facevo a mano,
solo quando me lo chiedeva lui.

Qui non si guarda la percentuale. La lavagna può dire -30%, non importa. Si guarda UNA COSA SOLA:
**ogni personaggio del team sta facendo il suo lavoro, nei tempi giusti, lasciando traccia?**

Ogni componente ha: un nome, un compito, un output che DEVE produrre, e una frequenza entro cui deve farlo.
Se qualcuno non risponde all'appello, viene detto per nome. Quando tutti rispondono per N ispezioni di fila,
la macchina è considerata in ordine — e solo allora ha senso guardare la lavagna.
Scrive ISPEZIONE.md + data/ispezione.json. €0.
"""
import json, os, re, glob, time, calendar, urllib.request

now = int(time.time())
STORICO = "data/ispezione.json"
ISPEZIONI_PER_FIDARSI = 6      # sei ispezioni di fila senza un difetto = la macchina è in ordine

# IL TEAM. Ogni riga: chi è, cosa fa, cosa deve produrre, entro quanti minuti, per quale chain.
TEAM = [
    # --- ruoli globali (valgono per tutte le chain) ---
    ("Verità",      "controlla che la percentuale non sia una favola",        "AUDIT.md",        90,  None),
    ("Security",    "nessuna credenziale nel repo pubblico",                  "SECURITY.md",     90,  None),
    ("CFO",         "che tutto continui a costare zero",                      "CFO.md",          90,  None),
    ("Memoria",     "ricorda cosa è già stato provato e bocciato",            "CONOSCENZA.md",   90,  None),
    ("Proposte",    "porta all'investitore ciò che aspetta una decisione",    "PROPOSTE.md",     90,  None),
    ("Operations",  "i meeting sui goal, ripara ciò che si ferma",            "LOOPS.md",        90,  None),
    ("Segretario",  "scrive il verbale della riunione",                       "TEAM.md",         90,  None),
    ("Statistico",  "com'è FATTA la percentuale (robustezza, out-of-time)",   "PERCENTUALE.md", 180,  None),
    ("Necroforo",   "quanti token muoiono e spariscono dai conti",            "MORTALITA.md",   180,  None),
    ("Giudice",     "prova le proposte sui dati mai visti (cassaforte)",      "VALIDAZIONE.md", 180,  None),
    ("Heartbeat",   "controlla che il MOTORE sia vivo, da fuori",             "HEARTBEAT.md",   180,  None),
    ("Forward Base","la catena che porta al trade su Base",                   "GOAL_BASE.md",   120,  None),
    # i quattro nati dalla consulenza esterna del 01/09: senza queste righe potevano fermarsi in silenzio
    ("Tassametro",  "misura quanto costa DAVVERO entrare e uscire",            "COSTI_REALI.md", 240,  None),
    ("Censore",     "ogni pool ha uno stato: morto o non raccolto?",           "CENSIMENTO.md",  240,  None),
    ("Perito",      "il token si può vendere? chi lo controlla?",              "SICUREZZA.md",   240,  None),
    ("Anagrafe",    "chi ha creato il token e i suoi precedenti",              "DEPLOYER.md",    240,  None),
    # Le piste aperte dopo la consulenza del 02/09. Se falliscono in silenzio nessuno se ne accorge:
    # un agente che non scrive il suo verbale non e' "in pausa", e' fermo — e va detto ad alta voce.
    ("Contabile",   "misura e modello dei costi devono dire lo stesso",        "COSTO_MODELLO.md", 300, None),
    ("Reputazione", "chi ha creato il token ha gia' combinato disastri?",      "CREATOR_GATE.md",  300, None),
    ("Talento",     "esiste un wallet che sa qualcosa? (excess vs comparabili)", "WALLET_SKILL.md", 300, None),
    ("Corrente",    "sta entrando capitale INDIPENDENTE, o e' una mano sola?", "FLUSSO_CLUSTER.md", 300, None),
    # --- ruoli per chain (girano a rotazione: tolleranza più larga) ---
    ("Esploratore", "prova strategie: entrata, stop, take profit, segnali",   "EXPLORER_{c}.md", 240, "base"),
    ("Esploratore", "prova strategie: entrata, stop, take profit, segnali",   "EXPLORER_{c}.md", 240, "solana"),
    ("Esploratore", "prova strategie sul pipeline completo",         "EXPLORER_ROBINHOOD.md",   240, "robinhood"),
    ("Ricercatore", "inventa segnali nuovi dai dati grezzi",                  "RICERCA_{c}.md",  360, "base"),
    ("Ricercatore", "inventa segnali nuovi dai dati grezzi",                  "RICERCA_{c}.md",  360, "solana"),
    ("Esploratore", "prova strategie: entrata, stop, take profit, segnali",   "EXPLORER_{c}.md", 480, "bsc"),
    ("Ricercatore", "inventa segnali nuovi dai dati grezzi",                  "RICERCA_{c}.md",  480, "robinhood"),
    ("Ricercatore", "inventa segnali nuovi dai dati grezzi",                  "RICERCA_{c}.md",  480, "bsc"),
]

# BUCO 2: non basta che il file sia FRESCO — deve contenere il segno di un lavoro vero. Un esploratore che
# scrive "0 strategie provate" è puntualissimo e non sta lavorando. Qui si cerca la prova nel testo.
PROVE_DI_LAVORO = {
    "EXPLORER_": (r"(\d+) strategie provate|(\d+) configurazioni provate", "strategie provate"),
    "RICERCA_": (r"(\d+) segnali nuovi messi alla prova", "segnali provati"),
    "CONOSCENZA.md": (r"(\d+) idee messe alla prova", "idee in archivio"),
    "LOOPS.md": (r"\| `(accumulo|percentuale|demo)", "meeting tenuti"),
    "PERCENTUALE.md": (r"\| \*\*(robinhood|base|solana|bsc)\*\*", "chain misurate"),
    "VALIDAZIONE.md": (r"\| (robinhood|base|solana) \|", "proposte giudicate"),
    "COSTI_REALI.md": (r"\| \$(\d+) \|", "size misurate"),
    "CENSIMENTO.md": (r"\| \*\*(base|solana|bsc)\*\* \|", "chain censite"),
    # si guarda l'ARCHIVIO totale, non i "nuovi di questo giro": quando il perito ha gia' controllato
    # tutti i token disponibili, i nuovi sono legittimamente zero — e' lavoro finito, non lavoro mancato.
    "SICUREZZA.md": (r"\| (?:base|solana|bsc) \| \d+ \| \*\*\d+\*\* \| \d+ \| (\d+) \|", "token in archivio"),
    "DEPLOYER.md": (r"token con creatore identificato \| \*\*(\d+)\*\*", "token con creatore"),
}


# "niente da fare" NON è "non ha lavorato": un componente che dichiara esplicitamente di non avere lavoro
# è sano. Senza questa distinzione il Giudice risultava guasto proprio dopo aver fatto bene il suo mestiere
# (aveva bocciato tutte le proposte, quindi non ne restavano da giudicare).
NIENTE_DA_FARE = ("Nessuna proposta", "niente da giudicare", "nessuna proposta aperta",
                  "Non ancora giudicabile", "non ancora giudicabile", "Campione insufficiente",
                  "troppo poche", "troppo pochi", "Non ancora sufficiente", "non basta per un verdetto",
                  "Nessun segnale nuovo", "non ha ancora")


def lavoro_vero(path):
    """(ok, dettaglio). Cerca dentro il file la prova che il componente abbia davvero prodotto qualcosa."""
    chiave = next((k for k in PROVE_DI_LAVORO if path.startswith(k) or path == k), None)
    if not chiave: return True, ""
    pat, etichetta = PROVE_DI_LAVORO[chiave]
    try: testo = open(path, errors="ignore").read()
    except Exception: return False, "file illeggibile"
    if any(f in testo for f in NIENTE_DA_FARE):
        return True, "niente da fare in questo giro (dichiarato)"
    trovati = re.findall(pat, testo)
    if not trovati: return False, f"nessun {etichetta} nel verbale"
    numeri = [int(x) for t in trovati for x in (t if isinstance(t, tuple) else (t,)) if str(x).isdigit()]
    if numeri and max(numeri) == 0: return False, f"0 {etichetta}: è puntuale ma non ha lavorato"
    return True, f"{max(numeri) if numeri else len(trovati)} {etichetta}"

# i dati devono CRESCERE, non solo esistere: l'accumulo è un componente come gli altri
ACCUMULO = [("base", 240), ("solana", 240), ("bsc", 360), ("robinhood", 360)]

# IL CERVELLO, per chain: e' il componente che produce LA PERCENTUALE. Non ispezionarlo voleva dire non
# controllare proprio il cuore del team 1. Si verifica sullo storico delle misure, non su un file .md.
# robinhood ha tolleranza larga: il suo storico (edge_history) scrive UNA riga al giorno, non a ore
CERVELLO = [("base", 240), ("solana", 240), ("bsc", 480), ("robinhood", 2160)]


def cervello():
    """ogni chain ha una misura recente della sua percentuale? (data/multichain_history.jsonl + edge_history)"""
    out = []
    per_chain = {}
    for f, key in (("data/multichain_history.jsonl", "chain"), ("data/edge_history.jsonl", None)):
        if not os.path.exists(f): continue
        try:
            for l in open(f):
                if not l.strip(): continue
                r = json.loads(l)
                ch = r.get("chain") if key else "robinhood"
                ts = r.get("ts")
                if not ts and r.get("date"):
                    try: ts = calendar.timegm(time.strptime(r["date"], "%Y-%m-%d"))
                    except Exception: ts = None
                if ch and ts: per_chain[ch] = max(per_chain.get(ch, 0), ts)
        except Exception: pass
    for ch, minuti in CERVELLO:
        t = per_chain.get(ch)
        if not t: out.append((ch, None, minuti, "❌ nessuna misura della percentuale"))
        else:
            eta = (now - t) / 60
            out.append((ch, eta, minuti, "✅ misurata" if eta <= minuti else
                        ("⚠️ in ritardo" if eta <= minuti * 2 else "❌ NON MISURA PIÙ")))
    return out


def quando(path):
    """l'ora scritta DENTRO il file (fonte vera: il timestamp del commit inganna, i merge lo spostano)."""
    if not os.path.exists(path): return None
    try:
        testa = open(path, errors="ignore").read(400)
    except Exception:
        return None
    m = re.search(r"(20\d\d-\d\d-\d\d) (\d\d):(\d\d) UTC", testa)
    if not m:
        return os.path.getmtime(path)
    try:
        # timegm e non mktime: i verbali scrivono l'ora UTC, e mktime la leggerebbe come ora LOCALE
        # (su una macchina italiana sono due ore di scarto: componenti sani sembrerebbero in ritardo)
        return calendar.timegm(time.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)}", "%Y-%m-%d %H:%M"))
    except Exception:
        return os.path.getmtime(path)


def interroga():
    esiti = []
    # UNA CHAIN CONGELATA NON HA UN ESPLORATORE FERMO: ha un esploratore a cui abbiamo VIETATO di
    # lavorare, e infatti non scrive il verbale. Il controllo sta QUI, prima di tutti i rami, e non
    # dentro ciascuno: ci ho provato ramo per ramo e ne restava sempre uno scoperto ("in ritardo",
    # poi "non lavora", poi "non risponde"). La terza volta che ripeti la stessa toppa, la toppa e'
    # nel posto sbagliato.
    _congelate = congelate()

    def _congelato(nome, chain):
        return bool(chain) and chain in _congelate and "splorat" in nome
    for nome, compito, file_t, minuti, chain in TEAM:
        f = file_t.format(c=chain) if chain else file_t
        if _congelato(nome, chain):
            esiti.append((nome, compito, chain, None, minuti,
                          "⏸️ congelato — non deve lavorare, aspetta il verdetto sull'holdout"))
            continue
        t = quando(f)
        if t is None:
            esiti.append((nome, compito, chain, None, minuti, "❌ NON HA MAI PRODOTTO NULLA")); continue
        eta = (now - t) / 60
        ok_lavoro, dettaglio = lavoro_vero(f)
        if not ok_lavoro:
            esiti.append((nome, compito, chain, eta, minuti, f"❌ NON LAVORA — {dettaglio}")); continue
        if eta <= minuti:
            esiti.append((nome, compito, chain, eta, minuti, f"✅ in orario · {dettaglio}" if dettaglio else "✅ in orario"))
        elif eta <= minuti * 2:
            esiti.append((nome, compito, chain, eta, minuti, "⚠️ in ritardo"))
        else:
            esiti.append((nome, compito, chain, eta, minuti, "❌ NON RISPONDE"))
    return esiti


def non_convocati():
    """CHI NON VIENE PIU' CHIAMATO? (aggiunto 02/09, dopo esserci cascati)

    Il 02/09 un push fatto da una copia vecchia del repo ha cancellato dal motore SEI agenti in un colpo:
    il guardiano delle credenziali, il CFO, la memoria, le proposte, il segretario e l'ispezione stessa.
    Nessuno era rotto. Nessuno andava in errore. Semplicemente non venivano piu' convocati, e per tre ore
    l'unico segno e' stato un verbale che invecchiava.

    L'ispezione guardava i VERBALI: sa dire "questo referto e' vecchio", non "questo agente non e' nella
    lista dei convocati". Sono due domande diverse, e la seconda arriva prima. Qui si controlla la lista:
    ogni agente che scrive un verbale deve essere chiamato da qualcuno."""
    import re
    chiamati = set()
    for f in glob.glob("agents/*loop*.py") + ["agents/engine.py"] + glob.glob(".github/workflows/*.yml"):
        try: chiamati |= set(re.findall(r"agents/(\w+)\.py", open(f).read()))
        except Exception: pass
    out = []
    for f in sorted(glob.glob("agents/*.py")):
        nome = os.path.basename(f)[:-3]
        if nome in chiamati: continue
        try: src = open(f).read()
        except Exception: continue
        # solo chi PRODUCE un verbale: le librerie condivise non devono essere convocate da nessuno
        if "SUPERATO" in src[:700]: continue    # chi si dichiara superato non deve essere convocato
        verbali = re.findall(r'open\("([A-Z_]+\.md)"', src)
        if verbali: out.append((nome, verbali[0]))
    return out


def congelate():
    """Le chain la cui configurazione e' stata CONGELATA in attesa del verdetto sull'holdout.

    Aggiunto il 03/09: appena congelata Robinhood, l'esploratore ha smesso di scrivere il suo verbale
    — giustamente, gli abbiamo vietato di riottimizzare — e l'ispezione l'ha segnalato "in ritardo".
    Un agente a cui abbiamo proibito di lavorare non e' un agente fermo. Confondere le due cose
    riempie la lavagna di allarmi finti, e gli allarmi finti sono il modo piu' veloce per smettere
    di guardare quelli veri."""
    try:
        c = json.load(open("data/criteri.json")).get("congelate", {})
        return {k for k, v in c.items() if not v.get("letto")}
    except Exception:
        return set()


def archivi_crescono():
    """GLI ARCHIVI STANNO CRESCENDO? (aggiunto 02/09)
    Il perito aveva esaurito i candidati e l'accumulo si era fermato di colpo — ma l'ispezione lo dava
    verde, perche' guardava l'ARCHIVIO TOTALE (863 token, numero alto e sano) senza accorgersi che aveva
    smesso di crescere. Un contatore fermo su un numero grande sembra salute: non lo e'."""
    out = []
    prec = {}
    if os.path.exists(STORICO):
        try: prec = json.load(open(STORICO)).get("archivi", {})
        except Exception: pass
    ora = {}
    for nome, pat in (("sicurezza", "data/sicurezza/*.jsonl"),):
        n = 0
        for f in glob.glob(pat):
            try: n += sum(1 for l in open(f) if l.strip())
            except Exception: pass
        ora[nome] = {"n": n, "ts": now}
        v = prec.get(nome) or {}
        vecchio, quando = v.get("n"), v.get("ts")
        if vecchio is None: out.append((nome, n, None, "🆕 prima misura"))
        elif n > vecchio: out.append((nome, n, n - vecchio, "✅ cresce"))
        elif quando and now - quando > 2 * 3600:
            out.append((nome, n, 0, "❌ FERMO da oltre 2 ore"))
        else:
            ora[nome]["ts"] = quando or now
            out.append((nome, n, 0, "⏳ nessun nuovo (normale entro 2h)"))
    return out, ora


def accumulo():
    """i dati stanno crescendo? un accumulo fermo è un componente rotto come gli altri."""
    out = []
    prec = {}
    if os.path.exists(STORICO):
        try: prec = json.load(open(STORICO)).get("accumulo", {})
        except Exception: pass
    ora = {}
    for ch, minuti in ACCUMULO:
        n = len(glob.glob(f"data/multichain/{ch}/candles/*.jsonl.gz")) + \
            len(glob.glob(f"data/multichain/{ch}/pulse/*.jsonl.gz"))
        ora[ch] = n
        # confronto su UN'ORA, non tra due ispezioni: l'ispezione gira ogni 15 min ma i collector ogni 30,
        # quindi "nessun token nuovo dall'ultima volta" era un falso allarme sistematico.
        v = prec.get(ch)
        vecchio = v.get("n") if isinstance(v, dict) else v
        quando = v.get("ts") if isinstance(v, dict) else None
        ora[ch] = {"n": n, "ts": (quando if (quando and n == vecchio and now - quando < 3900) else now)}
        if vecchio is None: out.append((ch, n, None, "🆕 prima misura"))
        elif n > vecchio: out.append((ch, n, n - vecchio, "✅ cresce"))
        elif quando and now - quando < 3900: out.append((ch, n, 0, "⏳ nessun token nuovo (normale entro l'ora)"))
        else: out.append((ch, n, 0, "⚠️ FERMO da oltre un'ora"))
    return out, ora


REPO = "nicolostancato-web/whale-radar"


def processi_vivi():
    """BUCO 3: i file possono essere freschi mentre il processo che li produce e' gia' morto — ce ne
    accorgeremmo solo ore dopo, quando i verbali iniziano a invecchiare. Qui si guarda direttamente se i
    workflow stanno girando ADESSO."""
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("WR_PAT", "")
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=25",
                                 headers={"Accept": "application/vnd.github+json"})
    if tok: req.add_header("Authorization", f"token {tok}")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            runs = json.load(r)["workflow_runs"]
    except Exception:
        return [("motore", None, "non verificabile ora"), ("ricerca", None, "non verificabile ora")]
    out = []
    for nome in ("engine", "ricerca"):
        vivi = [x for x in runs if x["name"] == nome and x["status"] in ("in_progress", "queued")]
        ultimi = [x for x in runs if x["name"] == nome]
        if vivi:
            out.append((nome, True, "in esecuzione"))
        elif ultimi:
            out.append((nome, False, f"FERMO — ultimo run {ultimi[0]['conclusion'] or '?'} "
                                     f"({ultimi[0]['created_at'][11:16]} UTC)"))
        else:
            out.append((nome, False, "mai partito"))
    return out


def controllo_qualita():
    """I DUE RUOLI CHE GIUDICANO IL LAVORO, non chi lo fa.
    L'ispezione fin qui chiedeva "hai scritto il tuo file?" — ma un componente puo' essere puntuale,
    produttivo, e sbagliare i conti. Questi due rispondono all'altra domanda: **quello che dice il team e' vero?**
      · VERITA' (auditor)   — il sistema si sta raccontando favole? (numeri non spiegati, regole riscritte)
      · GIUDICE (validatore) — le scoperte reggono sui dati che la ricerca non ha mai visto?
    Se uno dei due alza bandiera rossa, la macchina NON e' in ordine: non basta che tutti lavorino, devono
    anche avere ragione."""
    out = []
    # --- VERITA' ---
    critiche = None
    if os.path.exists("data/audit_flags.json"):
        try: critiche = json.load(open("data/audit_flags.json")).get("critiche", 0)
        except Exception: pass
    testo = ""
    if os.path.exists("AUDIT.md"):
        try: testo = open("AUDIT.md", errors="ignore").read(1200)
        except Exception: pass
    if critiche is None:
        out.append(("Verità", "il sistema si sta raccontando favole?", None, "❓ non si è ancora pronunciato"))
    elif critiche > 0:
        out.append(("Verità", "il sistema si sta raccontando favole?", False,
                    f"❌ **BANDIERA ROSSA**: {critiche} numeri che non si spiegano"))
    elif "DA CHIARIRE" in testo:
        out.append(("Verità", "il sistema si sta raccontando favole?", True,
                    "⚠️ qualcosa da chiarire, niente di critico"))
    else:
        out.append(("Verità", "il sistema si sta raccontando favole?", True, "✅ pulito: nessuna favola"))
    # --- GIUDICE ---
    giudicate = bocciate = 0; mai = True
    if os.path.exists("data/proposte.json"):
        try:
            for p in json.load(open("data/proposte.json")).get("proposte", []):
                v = p.get("validazione")
                if v:
                    mai = False; giudicate += 1
                    if v.get("robusta", -999) <= 0: bocciate += 1
        except Exception: pass
    aperte = 0
    if os.path.exists("data/proposte.json"):
        try: aperte = len([p for p in json.load(open("data/proposte.json")).get("proposte", [])
                           if p.get("stato") == "APERTA"])
        except Exception: pass
    if aperte == 0:
        out.append(("Giudice", "le scoperte reggono su dati mai visti?", True,
                    "✅ niente da giudicare: nessuna proposta aperta"))
    elif mai:
        out.append(("Giudice", "le scoperte reggono su dati mai visti?", False,
                    f"❌ ci sono {aperte} proposte e NESSUNA è stata giudicata in cassaforte"))
    else:
        out.append(("Giudice", "le scoperte reggono su dati mai visti?", True,
                    f"✅ {giudicate} giudicate, {bocciate} bocciate perché erano rumore"))
    return out


CHAINS = ["base", "solana", "robinhood", "bsc"]


def per_chain(esiti, cerv, acc):
    """Il LOOP 1 esiste in ogni chain: ognuna ha il suo team e merita un verdetto suo.
    Qui si raggruppa tutto quello che riguarda UNA chain: chi esplora, chi inventa segnali, il cervello che
    misura la percentuale, e i dati che devono crescere."""
    out = {}
    for ch in CHAINS:
        righe = [e for e in esiti if e[2] == ch]
        c = next((x for x in cerv if x[0] == ch), None)
        a = next((x for x in acc if x[0] == ch), None)
        problemi = [e for e in righe if e[5].startswith("❌")]
        if c and c[3].startswith("❌"): problemi.append(("Cervello", "misura la percentuale", ch, c[1], c[2], c[3]))
        ritardi = [e for e in righe if e[5].startswith("⚠️")]
        if not righe and not c:
            stato = "— nessun componente registrato"
        elif problemi:
            stato = f"🔴 {len(problemi)} non rispondono"
        elif ritardi or (a and a[3].startswith("⚠️ FERMO")):
            stato = "🟡 tutto vivo, qualcosa in ritardo"
        else:
            stato = "🟢 tutto in ordine"
        out[ch] = {"stato": stato, "righe": righe, "cervello": c, "accumulo": a,
                   "problemi": problemi, "ritardi": ritardi}
    return out


def main():
    esiti = interroga()
    cerv = cervello()
    qualita = controllo_qualita()
    proc = processi_vivi()
    acc, ora_acc = accumulo()
    arch, ora_arch = archivi_crescono()
    orfani = non_convocati()
    squadre = per_chain(esiti, cerv, acc)
    guasti = [e for e in esiti if e[5].startswith("❌")]
    proc_morti = [p for p in proc if p[1] is False]
    cerv_ko = [c for c in cerv if c[3].startswith("❌")]
    if cerv_ko: guasti = guasti + [(f"Cervello ({c[0]})", "misura la percentuale della chain", c[0], c[1], c[2], c[3]) for c in cerv_ko]
    arch_ko = [a for a in arch if a[3].startswith("❌")]
    if arch_ko: guasti = guasti + [(f"Archivio {a[0]}", "deve crescere", None, None, 0, a[3]) for a in arch_ko]
    if orfani:
        guasti = guasti + [(n, f"scrive {v} ma NESSUNO lo chiama", None, None, 0,
                            "❌ non e' nella lista dei convocati") for n, v in orfani]
    qual_ko = [q for q in qualita if q[2] is False]
    if qual_ko: guasti = guasti + [(q[0], q[1], None, None, 0, q[3]) for q in qual_ko]
    if proc_morti: guasti = guasti + [(p[0], "il processo che fa girare tutto", None, None, 0, "❌ " + p[2]) for p in proc_morti]
    ritardi = [e for e in esiti if e[5].startswith("⚠️")]

    st = {}
    if os.path.exists(STORICO):
        try: st = json.load(open(STORICO))
        except Exception: pass
    di_fila = (st.get("di_fila", 0) + 1) if not guasti and not ritardi else 0
    json.dump({"ts": now, "di_fila": di_fila, "guasti": len(guasti), "ritardi": len(ritardi),
               "accumulo": ora_acc, "archivi": ora_arch}, open(STORICO, "w"))

    if guasti:
        verdetto = f"🔴 **{len(guasti)} COMPONENTI NON RISPONDONO** — la macchina non è pronta"
    elif ritardi:
        verdetto = f"🟡 **{len(ritardi)} in ritardo** — nessuno è fermo, ma non sono nei tempi"
    elif di_fila >= ISPEZIONI_PER_FIDARSI:
        verdetto = f"🟢 **TUTTO IN ORDINE da {di_fila} ispezioni di fila** — la macchina gira, si può guardare la lavagna"
    else:
        verdetto = f"🟢 **tutti rispondono** — {di_fila}/{ISPEZIONI_PER_FIDARSI} ispezioni pulite di fila"

    prec_ts = st.get("ts")
    eta_ispezione = (now - prec_ts) / 60 if prec_ts else None
    avviso_self = ""
    if eta_ispezione and eta_ispezione > 150:
        avviso_self = (f"\n> ⚠️ **ATTENZIONE: l'ispezione precedente risale a {eta_ispezione/60:.1f} ore fa.** "
                       f"Doveva girare ogni ora: anche l'ispettore ha smesso di lavorare per un po'. "
                       f"Se stai leggendo un referto e non sai quando è stato scritto, non sai niente.\n")
    riepilogo = " · ".join(f"{ch}: {squadre[ch]['stato'].split(' ')[0]}" for ch in CHAINS)
    L = ["# 🔍 LOOP 0 · ISPEZIONE — il team sta lavorando?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · un giro ogni ora · "
         f"qui NON si guarda la percentuale: si guarda che ognuno faccia il suo lavoro*",
         avviso_self, "",
         f"## {verdetto}", "", f"**Per chain:** {riepilogo}", "",
         "## I team, chain per chain (LOOP 1)", ""]
    for ch in CHAINS:
        q = squadre[ch]
        L += [f"### {ch.upper()} — {q['stato']}", "",
              "| chi | cosa fa | ultimo lavoro | entro | |", "|---|---|---|---|---|"]
        for nome, compito, chain, eta, minuti, stato in q["righe"]:
            quando_txt = "mai" if eta is None else (f"{eta:.0f} min fa" if eta < 600 else f"{eta/60:.1f} ore fa")
            L.append(f"| **{nome}** | {compito} | {quando_txt} | {minuti} min | {stato} |")
        c = q["cervello"]
        if c:
            L.append(f"| **Cervello** | misura la percentuale della chain | "
                     f"{'mai' if c[1] is None else f'{c[1]:.0f} min fa'} | {c[2]} min | {c[3]} |")
        a = q["accumulo"]
        if a:
            L.append(f"| **Accumulo** | i dati devono crescere | {a[1]} token | — | {a[3]} |")
        L += [""]
    L += ["## I servizi comuni (valgono per tutte le chain)", "",
          "| chi | cosa fa | ultimo lavoro | entro | |", "|---|---|---|---|---|"]
    for nome, compito, chain, eta, minuti, stato in esiti:
        if chain: continue
        quando_txt = "mai" if eta is None else (f"{eta:.0f} min fa" if eta < 600 else f"{eta/60:.1f} ore fa")
        L.append(f"| **{nome}** | {compito} | {quando_txt} | {minuti} min | {stato} |")
    L += ["", "## E quello che dicono è VERO?", "",
          "> Gli altri rispondono alla domanda *stanno lavorando?*. Questi due rispondono all'altra, che è",
          "> altrettanto importante: *quello che producono è vero?* Un componente può essere puntuale,",
          "> produttivo, e avere torto.", "",
          "| chi | la domanda | risposta |", "|---|---|---|"]
    for nome, domanda, ok, dett in qualita:
        L.append(f"| **{nome}** | {domanda} | {dett} |")
    L += ["", "## Gli archivi crescono?", "", "| archivio | token | nuovi | |", "|---|---|---|---|"]
    for nome, n, delta, stato in arch:
        L.append(f"| {nome} | {n} | {'—' if delta is None else f'+{delta}'} | {stato} |")
    L += ["", "## I processi stanno girando?", "", "| processo | stato |", "|---|---|"]
    for nome, vivo, dett in proc:
        icona = "✅" if vivo else ("❓" if vivo is None else "❌")
        L.append(f"| **{nome}** | {icona} {dett} |")
    if guasti:
        L += ["## ⚠️ Chi non risponde all'appello", ""]
        for nome, compito, chain, eta, minuti, _ in guasti:
            et = f"{nome} ({chain})" if chain else nome
            L.append(f"- **{et}** — doveva lavorare entro {minuti} min, "
                     + ("non ha mai prodotto nulla" if eta is None else f"ultimo lavoro {eta/60:.1f} ore fa"))
        L += ["", "> Finché c'è anche un solo componente che non risponde, la macchina NON è pronta. Non ha",
              "> senso discutere della percentuale: prima si aggiusta il team.", ""]
    L += ["> **Come si legge:** qui la lavagna non conta. Può esserci scritto -30% e va benissimo. L'unica",
          "> domanda è se ogni personaggio del team sta facendo il suo lavoro, nei tempi, lasciando traccia.",
          f"> Quando l'ispezione è pulita per **{ISPEZIONI_PER_FIDARSI} giri di fila**, la macchina è in ordine",
          "> e possiamo tornare a guardare i numeri."]
    open("ISPEZIONE.md", "w").write("\n".join(L))
    print(f"ISPEZIONE | {verdetto[:52]} | {len(guasti)} guasti, {len(ritardi)} ritardi | pulite di fila: {di_fila}",
          flush=True)


if __name__ == "__main__":
    main()
