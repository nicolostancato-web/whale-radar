#!/usr/bin/env python3
"""
AUDITOR — il REVISORE che controlla che il sistema non stia BARANDO.

Perche' esiste (30/08, Nicolo cita l'esperimento OpenAI): un loop potente con un goal preciso NON risolve il
problema, trova la strada piu' breve per far RISULTARE il goal raggiunto. E' il "reward hacking". A noi e' gia'
successo: il paper da €323k di crypto-radar era un artefatto — il sistema sembrava vincente senza esserlo.
Piu' i loop diventano autonomi, piu' servono controlli che i loop NON possono toccare. Questo e' quel controllo.

Regola: l'auditor non ottimizza niente e non ripara niente. Guarda e firma. Se qualcosa non torna, ALZA
BANDIERA ROSSA e i loop non possono salire di scala finche' non e' chiarita.
Scrive AUDIT.md + data/audit_flags.json. Sola lettura. €0.
"""
import json, os, time, gzip, glob

now = int(time.time())
FLAGS = "data/audit_flags.json"


def check_forward_puro(nome, path):
    """Il demo deve entrare SOLO su token nati dopo l'apertura del conto. E' la regola che rende il numero
    vero: se salta, stiamo misurando lo storico (cioe' ci stiamo raccontando una favola)."""
    if not os.path.exists(path): return None
    try: st = json.load(open(path))
    except Exception: return (nome, "stato del conto illeggibile", "ALTA")
    start = st.get("start_ts", 0)
    for pos in st.get("open", []):
        # le posizioni portano il timestamp d'uscita: se e' precedente all'apertura del conto e' storico
        if pos.get("xt", now) < start:
            return (nome, f"posizione con uscita PRIMA dell'apertura del conto ({pos.get('pool','?')[:10]}): non e' forward", "CRITICA")
    return None


def check_equity_coerente(nome, path):
    """Il saldo deve essere spiegato dai trade. Un salto senza trade e' un numero inventato."""
    if not os.path.exists(path): return None
    try: st = json.load(open(path))
    except Exception: return None
    eq = st.get("bal", 0) + sum(x.get("size", 0) for x in st.get("open", []))
    chiusi = st.get("closed", 0); aperte = len(st.get("open", []))
    if chiusi == 0 and aperte == 0 and abs(eq - 100.0) > 0.01:
        return (nome, f"saldo €{eq:.2f} con ZERO trade: il numero non e' spiegato da nessuna operazione", "CRITICA")
    if eq > 100 * (1 + chiusi * 3):      # nessun trade puo' fare piu' di ~3x sul capitale allocato
        return (nome, f"saldo €{eq:.0f} troppo alto per {chiusi} trade chiusi: sospetto artefatto", "ALTA")
    return None


def check_percentuale_credibile():
    """Un salto enorme della percentuale da un ciclo all'altro non e' un miglioramento: e' un bug o un imbroglio.
    (E' esattamente cosi' che si presento' il €323k: di colpo, senza una ragione.)"""
    out = []
    for f, campo, nome in (("data/edge_history.jsonl", "sel_no3", "robinhood"),
                           ("data/multichain_history.jsonl", "robusta", "multichain")):
        if not os.path.exists(f): continue
        try: recs = [json.loads(l) for l in open(f) if l.strip()]
        except Exception: continue
        for ch in set(r.get("chain", nome) for r in recs):
            serie = [r for r in recs if r.get("chain", nome) == ch][-6:]
            for a, b in zip(serie, serie[1:]):
                va, vb = a.get(campo), b.get(campo)
                if va is None or vb is None: continue
                if abs(vb - va) > 80:
                    out.append((f"percentuale-{ch}", f"salto da {va:+.0f}% a {vb:+.0f}% tra due misure: da spiegare", "ALTA"))
    return out


def check_parametri_tracciati():
    """I parametri di strategia sono DECISIONI umane. Se cambiano senza lasciare traccia, il sistema si sta
    riscrivendo le regole da solo — che e' il modo piu' elegante di barare."""
    out = []
    for f in glob.glob("data/strategy*.json"):
        if not os.path.exists("data/strategy_history.jsonl"): break
        try:
            cur = json.load(open(f))
            hist = [json.loads(l) for l in open("data/strategy_history.jsonl") if l.strip()]
        except Exception: continue
        if not hist: continue
        chiavi = ("tp1", "tp2", "trail", "hard", "entry_h")
        visti = [{k: h.get(k) for k in chiavi} for h in hist]
        ora = {k: cur.get(k) for k in chiavi}
        if ora not in visti and any(v is not None for v in ora.values()):
            out.append((os.path.basename(f), f"parametri attuali {ora} non presenti nello storico: cambio non tracciato", "MEDIA"))
    return out


def check_insider_onesto():
    """La soglia dichiarata PRIMA (40 casi, p<0.01) non deve essere ammorbidita per far uscire un si'."""
    p = "data/insider_scores.json"
    if not os.path.exists(p): return None
    try: d = json.load(open(p))
    except Exception: return None
    if d.get("min_ev", 2) < 2 or d.get("good", 0.6) < 0.5:
        return ("insider", f"soglie allentate (min_ev={d.get('min_ev')}, good={d.get('good')}): sospetto adattamento al risultato", "ALTA")
    return None


# ============================================================================================
# LE CICATRICI — ogni errore che ci ha fregato una volta diventa un controllo che gira per sempre.
#
# Il 3/9 Nicolo' ha detto: "non ci illudiamo, tanto hai un agente che sa se ci stiamo illudendo".
# Mezza verita', e la meta' che manca conta. Questo revisore l'ho scritto io: controlla i modi di
# illudersi che AVEVO PENSATO, ed e' cieco su quelli che non mi erano venuti in mente. La prova:
# in tre giorni sono usciti quattro errori gravi e TUTTI E QUATTRO sono passati sotto il naso di
# questo file, che intanto scriveva "nessun salto sospetto". Non ha fallito: non sapeva di cercarli.
#
# Non diventa onnisciente scrivendone uno piu' grosso — lo scriverei sempre io. Ma ogni illusione
# che ci frega una volta puo' smettere di fregarci: basta trasformarla in un controllo permanente.
# Sotto ci sono le quattro di questi giorni. Quando ne troveremo una quinta, si aggiunge qui.
# ============================================================================================

def cicatrice_costo_coerente():
    """3/9 — dicevamo "i costi li abbiamo misurati" e nei conti ne usavamo un altro, 8 volte piu' alto.
    Con quel metro avevamo dichiarato morte quattro chain.

    Attenzione a COSA si controlla: la prima versione verificava che metro.py fosse coerente con le
    sue misure — un controllo inutile, perche' metro.py le misure le legge, non puo' divergerne.
    Il rischio vero e' un altro, ed e' quello che era successo davvero: un agente che si RISCRIVE i
    costi a mano e scavalca il metro. Basta un `XS = 0.15` dimenticato in un file e quel file giudica
    con un metro suo, mentre tutti gli altri usano quello misurato. Qui si cerca proprio quello."""
    import re
    out = None
    sospetti = []
    for f in glob.glob("agents/*.py"):
        nome = os.path.basename(f)
        if nome in ("metro.py", "auditor.py"): continue
        try: src = open(f).read()
        except Exception: continue
        for m in re.finditer(r"^\s*(ES|XS|SLIPPAGE|SLIP)\s*=\s*([0-9.]+)", src, re.M):
            val = float(m.group(2))
            if val > 0.001 and "_M." not in m.group(0) and "metro" not in m.group(0):
                sospetti.append(f"{nome}: {m.group(1)}={val}")
    if sospetti:
        out = ("costi-scritti-a-mano",
               "questi file si riscrivono i costi invece di usare il metro misurato — "
               + "; ".join(sospetti[:4]), "CRITICA")
    return out


def cicatrice_disastri_coerenti():
    """3/9 — il cancello dei creator trovava l'1% di disastri mentre la mortalita' ne misura il 12-24%.
    I due numeri non potevano essere entrambi veri: i token spariti senza prezzo non entravano nel
    conto, perche' per entrarci serviva un prezzo. Se tornano a divergere, e' lo stesso buco."""
    try:
        txt = open("CREATOR_GATE.md").read()
        import re
        quote = [float(x) for x in re.findall(r"\*\*(\d+)%\*\*", txt)]
        mort = open("MORTALITA.md").read()
        tassi = [float(x) for x in re.findall(r"\*\*(\d+)%\*\*", mort)]
        if quote and tassi:
            peggio = max(quote); atteso = min(tassi)
            if peggio < atteso / 3:
                return ("disastri-vs-mortalita",
                        f"il cancello vede al massimo {peggio:.0f}% di token finiti male, ma la mortalita' "
                        f"ne misura almeno {atteso:.0f}%: i token spariti stanno sparendo anche dal conto",
                        "ALTA")
    except Exception: pass
    return None


def cicatrice_placebo_obbligatorio():
    """3/9 — il flusso dei cluster sembrava +4,4%. Poi il controllo all'indietro: +307% PRIMA del
    segnale. Non prevedeva un rialzo, ne riconosceva uno gia' avvenuto. Da allora ogni verbale che
    dichiara un segnale DEVE mostrare anche il placebo all'indietro."""
    out = []
    for f in ("FLUSSO_CLUSTER.md", "WALLET_SKILL.md"):
        try:
            t = open(f).read()
        except Exception:
            continue
        dichiara = "Esiste informazione" in t or "cancello funziona" in t
        if dichiara and "placebo" not in t.lower() and "indietro" not in t.lower():
            out.append((f, "dichiara un segnale senza mostrare il controllo all'indietro: "
                           "potrebbe essere momentum gia' avvenuto", "ALTA"))
    return out


def cicatrice_trappole_a_zero():
    """3/9 — un honeypot tiene il prezzo su: il backtest vedeva uno stop a -40% e registrava -40%,
    quando la realta' e' -100%. Se l'elenco delle trappole si svuota o non viene piu' usato, quelle
    perdite tornano silenziosamente a sembrare piccole."""
    try:
        d = json.load(open("data/trappole.json"))
        n = len(d.get("pool") or {})
        eta_h = (now - int(d.get("ts") or 0)) / 3600
        if n == 0:
            return ("trappole-vuote", "nessun token marcato come trappola: o non ce ne sono (improbabile) "
                                      "o l'elenco non viene piu' aggiornato", "ALTA")
        if eta_h > 24:
            return ("trappole-vecchie", f"l'elenco delle trappole non si aggiorna da {eta_h:.0f} ore", "MEDIA")
    except Exception:
        return ("trappole-mancanti", "l'elenco delle trappole non esiste: le perdite totali tornano a "
                                     "essere contate come stop normali", "ALTA")
    return None


def cicatrice_archivi_non_arretrano():
    """4/9 — l'archivio dei costi e' passato da 800 a 609 misure senza che nessuno cancellasse niente.

    Causa: due processi diversi scrivevano lo stesso file e ognuno, risolvendo i conflitti, teneva la
    PROPRIA copia. Chi pubblicava per ultimo riportava indietro l'archivio distruggendo misure che non
    aveva mai toccato. Nessun errore, nessuna eccezione, nessun allarme: i numeri scendevano mentre il
    codice era corretto — ed e' il tipo di guasto piu' insidioso che esista.

    Qui non si controlla LA CAUSA (due scrittori) ma IL SINTOMO: un archivio che cresce non deve mai
    arretrare. Cosi' il controllo vale anche per le cause che non abbiamo ancora incontrato — che sono
    quelle che ci faranno male davvero."""
    ACCUMULANO = {"costi": "data/costi/*.json", "sicurezza": "data/sicurezza/*.jsonl",
                  "rubrica": "data/multichain/*/token_map.json", "trappole": "data/trappole.json"}
    try: prec = json.load(open(FLAGS)).get("archivi", {})
    except Exception: prec = {}
    ora, out = {}, []
    for nome, pat in ACCUMULANO.items():
        tot = 0
        for f in glob.glob(pat):
            try: tot += os.path.getsize(f)
            except Exception: pass
        ora[nome] = tot
        vecchio = prec.get(nome)
        # -2% di tolleranza: una potatura dichiarata puo' limare, un crollo no
        if vecchio and tot < vecchio * 0.98:
            out.append((f"archivio-{nome}",
                        f"e' ARRETRATO: da {vecchio/1024:.0f} KB a {tot/1024:.0f} KB "
                        f"({(tot/vecchio-1)*100:+.0f}%). Un archivio che accumula non torna indietro "
                        f"da solo: qualcuno sta sovrascrivendo il lavoro di qualcun altro", "CRITICA"))
    return out, ora


def main():
    flags = []
    for nome, path in (("demo-robinhood", "data/demo_live_state.json"),
                       ("demo-base", "data/demo_live_base_state.json")):
        for f in (check_forward_puro(nome, path), check_equity_coerente(nome, path)):
            if f: flags.append(f)
    flags += check_percentuale_credibile()
    flags += check_parametri_tracciati()
    f = check_insider_onesto()
    if f: flags.append(f)
    # LE CICATRICI: i quattro errori che ci hanno gia' fregato, ora controllati per sempre
    for f in (cicatrice_costo_coerente(), cicatrice_disastri_coerenti(), cicatrice_trappole_a_zero()):
        if f: flags.append(f)
    flags += cicatrice_placebo_obbligatorio()
    arretrati, dim_archivi = cicatrice_archivi_non_arretrano()
    flags += arretrati

    critiche = [x for x in flags if x[2] == "CRITICA"]
    json.dump({"ts": now, "n": len(flags), "critiche": len(critiche), "archivi": dim_archivi,
               "flags": [{"dove": a, "cosa": b, "gravita": c} for a, b, c in flags]}, open(FLAGS, "w"))

    verdetto = ("🟢 **PULITO** — nessun segno che il sistema si stia raccontando favole" if not flags else
                "🔴 **BANDIERA ROSSA** — c'e' almeno un numero che non si spiega" if critiche else
                "🟡 **DA CHIARIRE** — niente di grave, ma qualcosa va guardato")
    L = ["# 🕵️ AUDIT — il sistema sta barando?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · controlli che i loop NON possono toccare*", "",
         f"## Verdetto: {verdetto}", "",
         "> Un loop potente con un goal preciso non risolve il problema: trova la strada piu' corta per far",
         "> RISULTARE il goal raggiunto. A noi e' gia' successo (il paper da €323k era un artefatto). Questi",
         "> controlli esistono per accorgercene PRIMA di metterci soldi veri.", ""]
    if flags:
        L += ["| dove | cosa non torna | gravita' |", "|---|---|---|"]
        L += [f"| `{a}` | {b} | {c} |" for a, b, c in flags]
    else:
        L += ["**Controlli passati:**", "",
              "- i conti demo entrano solo su token nati DOPO l'apertura (forward puro, niente storico)",
              "- il saldo e' spiegato dai trade realmente chiusi",
              "- nessun salto sospetto della percentuale tra due misure",
              "- i parametri di strategia hanno tutti una traccia (nessuna auto-riscrittura delle regole)",
              "- le soglie dichiarate prima dell'esperimento insider non sono state ammorbidite"]
    L += ["", "> L'auditor non ripara e non ottimizza: guarda e firma. Se alza bandiera rossa, i loop non",
          "> possono salire di scala finche' un umano non ha chiarito il numero."]
    open("AUDIT.md", "w").write("\n".join(L))
    print(f"AUDITOR | {verdetto[:40]} | {len(flags)} segnalazioni ({len(critiche)} critiche)", flush=True)


if __name__ == "__main__":
    main()
