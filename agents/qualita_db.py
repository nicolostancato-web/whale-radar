#!/usr/bin/env python3
"""
QUALITA_DB — il controllo continuo del TERRENO. Non raccoglie: verifica che quello che raccogliamo
sia utilizzabile.

PERCHE' ESISTE (14/09, idea di Nicolo). Fin qui il database veniva controllato solo quando qualcuno
decideva di controllarlo. I difetti trovati nelle ultime 48 ore erano li' da SETTIMANE:
  - l'embargo che azzerava le feature sugli scambi nel 92% delle righe
  - 4.083 file di scambi orfani su Robinhood, che non si uniscono a niente
  - la join serie->scambi al 9%
Nessuno di questi ha mai fatto rumore. Li ha trovati un audit a mano, perche' e' stato chiesto.

La differenza fra questo e gli altri controlli: gli altri chiedono "il sistema gira?". Questo chiede
**"quello che sta entrando serve a qualcosa?"**. Un collettore che funziona benissimo e produce dati
che non si uniscono a niente, per questo controllo e' un FALLIMENTO.

Ogni controllo ha un esito esplicito: PASSA / ATTENZIONE / FALLISCE, con il numero che lo dimostra.
Un controllo che non riesce a misurare dice NON MISURABILE — mai "passa" per assenza di prove.

Sola lettura. €0.
"""
import json, glob, gzip, os, sys, time, statistics as st
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CHAINS = ("base", "solana", "robinhood")
ESITI = []


def check(nome, stato, numero, perche):
    ESITI.append({"nome": nome, "stato": stato, "numero": numero, "perche": perche})


def serie_di(ch):
    s = {os.path.basename(f).replace(".jsonl.gz", "") for f in glob.glob(f"data/multichain/{ch}/candles/*.gz")}
    s |= {os.path.basename(f).replace(".jsonl.gz", "") for f in glob.glob(f"data/multichain/{ch}/pulse/*.gz")}
    return s


def scambi_di(ch):
    return {os.path.basename(f).replace(".jsonl.gz", "") for f in glob.glob(f"data/multichain/{ch}/trades/*.gz")}


def c_orfani():
    """Dati raccolti che non si uniscono a niente: lavoro fatto e buttato."""
    for ch in CHAINS:
        s, t = serie_di(ch), scambi_di(ch)
        if not t:
            check(f"{ch}: scambi orfani", "NON MISURABILE", 0, "nessun file di scambi"); continue
        orf = len(t - s)
        q = orf / len(t) * 100
        stato = "PASSA" if q < 20 else ("ATTENZIONE" if q < 50 else "FALLISCE")
        check(f"{ch}: scambi orfani", stato, round(q, 1),
              f"{orf} file su {len(t)} non si uniscono a nessuna serie di prezzo")


def c_join():
    """Quante serie hanno anche gli scambi: e' il numero che decide quali domande possiamo fare."""
    for ch in CHAINS:
        s, t = serie_di(ch), scambi_di(ch)
        if not s:
            check(f"{ch}: serie con scambi", "NON MISURABILE", 0, "nessuna serie"); continue
        q = len(s & t) / len(s) * 100
        stato = "PASSA" if q >= 60 else ("ATTENZIONE" if q >= 25 else "FALLISCE")
        check(f"{ch}: serie con scambi", stato, round(q, 1), f"{len(s & t)} su {len(s)}")


def c_feature_vive():
    """IL CONTROLLO CHE MANCAVA. Una feature costante non e' una feature: e' una colonna. Se le
    variabili sugli scambi non variano, ogni risultato che le riguarda e' privo di significato."""
    try:
        import multichain_brain as B
    except Exception as e:
        check("feature sugli scambi vive", "NON MISURABILE", 0, f"non riesco a caricare il cervello: {type(e).__name__}")
        return
    neutro = [0.5, 0.0, 0.0, 1.0]
    for ch in CHAINS:
        try:
            righe = B.load_rows(ch)
        except Exception:
            righe = []
        if len(righe) < 50:
            check(f"{ch}: feature scambi vive", "NON MISURABILE", len(righe), "meno di 50 righe"); continue
        vive = sum(1 for r in righe if [round(v, 6) for v in r["f"][6:10]] != neutro)
        q = vive / len(righe) * 100
        stato = "PASSA" if q >= 50 else ("ATTENZIONE" if q >= 20 else "FALLISCE")
        check(f"{ch}: feature scambi vive", stato, round(q, 1),
              f"solo {vive} righe su {len(righe)} hanno scambi veri; le altre usano il valore di ripiego")


def c_finestra_embargo():
    """La finestra fra entrata e ritardo: se e' negativa, nessuno scambio puo' entrare, MAI."""
    try:
        import multichain_brain as B
        fin = B.ENTRY_H * 3600 - B.RITARDO_OSS
    except Exception as e:
        check("finestra dell'embargo", "NON MISURABILE", 0, f"{type(e).__name__}"); return
    stato = "PASSA" if fin > 0 else "FALLISCE"
    check("finestra dell'embargo", stato, round(fin / 3600, 1),
          f"entrata a +{B.ENTRY_H}h meno ritardo {B.RITARDO_OSS/3600:.1f}h" +
          ("" if fin > 0 else " → NESSUNO scambio puo' mai entrare"))


def c_duplicati():
    try:
        import multichain_brain as B
    except Exception:
        check("entita' duplicate", "NON MISURABILE", 0, "cervello non caricabile"); return
    for ch in CHAINS:
        try: righe = B.load_rows(ch)
        except Exception: righe = []
        if not righe: continue
        c = Counter(r["pool"] for r in righe)
        dup = sum(v - 1 for v in c.values() if v > 1)
        check(f"{ch}: entita' duplicate", "PASSA" if dup == 0 else "FALLISCE", dup,
              f"{len(righe)} righe, {len(c)} pool distinti")


def c_timbro():
    """I dati nuovi portano il timbro di acquisizione? Senza, la verifica point-in-time muore di nuovo."""
    for ch in CHAINS:
        fs = sorted(glob.glob(f"data/multichain/{ch}/trades/*.gz"), key=os.path.getmtime, reverse=True)[:25]
        con = tot = 0
        for f in fs:
            try:
                for l in gzip.open(f, "rt"):
                    if not l.strip(): continue
                    d = json.loads(l); tot += 1
                    if d.get("acq"): con += 1
                    break
            except Exception: pass
        if not tot:
            check(f"{ch}: timbro di acquisizione", "NON MISURABILE", 0, "nessun file leggibile"); continue
        q = con / tot * 100
        check(f"{ch}: timbro di acquisizione", "PASSA" if q >= 50 else "ATTENZIONE", round(q, 1),
              f"{con} file su {tot} fra i piu' recenti hanno il campo acq")


def c_freschezza():
    """Un archivio che non cresce e' fermo, e da fuori sembra pieno.

    NON SI USA LA DATA DEL FILE (14/09). Alla prima esecuzione questo controllo ha dichiarato "4.691
    file toccati nelle ultime 3 ore su 4.691": verde pieno, e falso — la cartella era appena stata
    clonata, quindi TUTTI i file avevano la data di adesso. La data di modifica racconta l'ultima
    volta che il file e' stato copiato, non quando il dato e' entrato. Qui si guarda DENTRO i file:
    l'istante piu' recente che contengono, che nessuna copia puo' falsificare."""
    now = time.time()
    for ch in CHAINS:
        fs = glob.glob(f"data/multichain/{ch}/trades/*.gz") + glob.glob(f"data/multichain/{ch}/pulse/*.gz")
        if not fs:
            check(f"{ch}: freschezza", "NON MISURABILE", 0, "nessun file"); continue
        import random
        camp = random.Random(1).sample(fs, min(60, len(fs)))
        ultimo = 0; letti = 0
        for f in camp:
            try:
                for l in gzip.open(f, "rt"):
                    if not l.strip(): continue
                    d = json.loads(l)
                    v = d.get("acq") or d.get("ts")
                    if v: ultimo = max(ultimo, int(v))
                letti += 1
            except Exception: pass
        if not letti or not ultimo:
            check(f"{ch}: freschezza", "NON MISURABILE", 0, "nessun istante leggibile dentro i file"); continue
        ore = (now - ultimo) / 3600
        stato = "PASSA" if ore < 6 else ("ATTENZIONE" if ore < 24 else "FALLISCE")
        check(f"{ch}: freschezza", stato, round(ore, 1),
              f"il dato piu' recente nel campione ha {ore:.1f} ore (letto DENTRO i file, non dalla data del file)")


def c_storico():
    """LO STORICO DALLA CATENA: quanto copre, e soprattutto SERVE?

    Un archivio nuovo che nessuno legge e' peso, non ricchezza — e' successo con wallet_scores.json,
    3,2 MB mai aperti da nessun modello. Qui si misura la cosa che conta: per quante righe
    valutabili lo storico porta abbastanza scambi PRIMA del momento in cui compreremmo."""
    try:
        import multichain_brain as B, classe_ricca as R
    except Exception as e:
        check("storico: utilita'", "NON MISURABILE", 0, f"non riesco a caricare: {type(e).__name__}"); return
    for ch in ("base", "robinhood"):
        fs = glob.glob(f"data/multichain/{ch}/storico/*.jsonl.gz")
        if not fs:
            check(f"{ch}: storico dalla catena", "FALLISCE", 0, "nessun file: la raccolta non gira")
            continue
        check(f"{ch}: storico dalla catena", "PASSA", len(fs), f"{len(fs)} pool con storia dalla catena")
        # DUE DOMANDE DIVERSE, E CONFONDERLE MENTE (15/09). La prima versione misurava su tutte le
        # righe e dava 0,2%: sembrava che lo storico non servisse. Falso — misurava soprattutto
        # righe che lo storico non ce l'hanno ancora. Sulle righe che CE L'HANNO il numero e' 94%.
        # Un denominatore sbagliato fa sembrare inutile una cosa che funziona.
        try:
            righe = B.load_rows(ch)
            con = [r for r in righe if os.path.exists(f"data/multichain/{ch}/storico/{r['pool']}.jsonl.gz")]
            cop = len(con) / max(1, len(righe)) * 100
            check(f"{ch}: storico, quante righe copre", "PASSA" if cop >= 25 else "ATTENZIONE",
                  round(cop, 1), f"{len(con)} righe su {len(righe)} hanno la storia dalla catena")
            if len(con) < 30:
                check(f"{ch}: storico utile", "NON MISURABILE", len(con),
                      "meno di 30 righe coperte: non si giudica"); continue
            camp = con[:300]
            dato = sum(1 for r in camp
                       if len([t for t in R.scambi(ch, r["pool"]) if t["ts"] <= r["ent"]]) >= 6)
            q = dato / len(camp) * 100
            stato = "PASSA" if q >= 60 else ("ATTENZIONE" if q >= 25 else "FALLISCE")
            check(f"{ch}: storico utile", stato, round(q, 1),
                  f"sulle righe COPERTE: {dato} su {len(camp)} hanno almeno 6 scambi prima dell'entrata")
        except Exception as e:
            check(f"{ch}: storico utile", "NON MISURABILE", 0, f"{type(e).__name__}")


def main():
    for f in (c_finestra_embargo, c_feature_vive, c_storico, c_join, c_orfani, c_duplicati, c_timbro, c_freschezza):
        try: f()
        except Exception as e:
            check(f.__name__, "NON MISURABILE", 0, f"il controllo stesso e' fallito: {type(e).__name__}")

    falliti = [e for e in ESITI if e["stato"] == "FALLISCE"]
    attenz = [e for e in ESITI if e["stato"] == "ATTENZIONE"]
    nonmis = [e for e in ESITI if e["stato"] == "NON MISURABILE"]
    L = ["# 🧱 QUALITÀ DEL TERRENO — il database serve a qualcosa?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · controllo continuo · €0*", "",
         "> Gli altri controlli chiedono **«il sistema gira?»**. Questo chiede **«quello che sta",
         "> entrando serve a qualcosa?»**. Un collettore che funziona benissimo e produce dati che non",
         "> si uniscono a niente, qui è un **fallimento**.", "",
         f"## {len(falliti)} falliti · {len(attenz)} da guardare · {len(nonmis)} non misurabili", "",
         "| controllo | esito | numero | perché |", "|---|---|---|---|"]
    ordine = {"FALLISCE": 0, "ATTENZIONE": 1, "NON MISURABILE": 2, "PASSA": 3}
    for e in sorted(ESITI, key=lambda x: (ordine.get(x["stato"], 9), x["nome"])):
        icona = {"FALLISCE": "🔴", "ATTENZIONE": "🟡", "PASSA": "🟢", "NON MISURABILE": "❓"}[e["stato"]]
        L.append(f"| {e['nome']} | {icona} **{e['stato']}** | {e['numero']} | {e['perche']} |")
    L += ["", "> **«Non misurabile» non è «passa».** Un controllo che non riesce a misurare non ha",
          "> assolto niente: ha solo taciuto.", ""]
    if falliti:
        L += ["## Il primo da riparare", "",
              f"> 🔴 **{falliti[0]['nome']}** — {falliti[0]['perche']}", "",
              "> Finché questo fallisce, ogni risultato che dipende da quel dato non significa quello",
              "> che sembra significare."]
    open("QUALITA_DB.md", "w").write("\n".join(L))
    print(f"QUALITA_DB | falliti {len(falliti)} | attenzione {len(attenz)} | non misurabili {len(nonmis)}", flush=True)


if __name__ == "__main__":
    main()
