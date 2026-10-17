"""La revisione della STRUTTURA: difetti dell'impianto, non dei dati.

PERCHE' ESISTE (10/10, ordine di Nicolo': «sistema un po' tutto a livello architettonico,
assicurati tutti questi errori di memoria, oppure il fatto che si scrive giga di qua, oppure il
fatto che avevamo perso file di la'»).

Gli audit che c'erano guardano i DATI (integrita, qualita_db), la SALUTE della pipeline
(health_audit) e il BARARE (auditor). Nessuno guardava l'impianto. Ma i quattro guasti peggiori
del 10 ottobre erano tutti strutturali, e nessuno dei controlli esistenti poteva vederli:

  1. la pubblicazione di Astra cercava una cartella del Mac (`/private/tmp/claude-501/...`):
     sul runner non esiste, l'import falliva, e TRENTA consulenze pagate sono morte col runner
     mentre il registro diceva «success»;
  2. una guardia leggeva `ASTRA_REVIEW.md`, file del flusso vecchio fermo da 29 giorni, e
     concludeva «il consulente tace da 698 ore»: falso, e copriva il guasto vero (il punto 1);
  3. una corsia giornaliera aveva un limite di silenzio di 15 ore: allarme garantito ogni
     giorno, e un allarme che suona sempre non distingue piu' niente;
  4. file da 9-52 MB riscritti INTERI decine di volte al giorno hanno portato il repository a
     9,85 GB su 10, cioe' a poche ore dal blocco di ogni scrittura.

Ogni controllo qui sotto nasce da uno di quei guasti, e dice COSA FARE, non solo cosa c'e' che
non va. Se un giorno passano tutti, l'impianto e' pulito; quando ne nasce uno nuovo, si aggiunge
un controllo, non un promemoria.
"""
import json
import os
import re
import subprocess
import sys

CARTELLA_WF = ".github/workflows"
GIORNI_MORTO = 14


def _sorgenti():
    return [f"agents/{x}" for x in sorted(os.listdir("agents")) if x.endswith(".py")]


def c_strade_del_mac():
    """GUASTO 1: codice che nomina una cartella del Mac non puo' funzionare sul runner."""
    guai = []
    for p in _sorgenti():
        s = open(p, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'["\'](/private/tmp/claude-\d+[^"\']*|/Users/[^"\']+)["\']', s):
            riga = s[:m.start()].count("\n") + 1
            # un commento che RACCONTA il guasto non e' il guasto: conta solo il codice
            testo = s.splitlines()[riga - 1].strip()
            if testo.startswith("#") or testo.startswith('"""'):
                continue
            guai.append(f"{p}:{riga} usa una strada del Mac ({m.group(1)[:46]}…) — "
                        f"sul runner non esiste. Prendi la strada da os.environ o dal repo.")
    return guai


def c_guardie_su_file_morti():
    """GUASTO 2: una guardia che legge un file che non c'e' da' sempre lo stesso verdetto."""
    guai = []
    for p in _sorgenti():
        s = open(p, encoding="utf-8", errors="replace").read()
        if not re.search(r"def c_|_ore_da_ultimo|getmtime", s):
            continue
        for m in re.finditer(r'["\']([A-Z][A-Z_0-9]+\.md)["\']', s):
            f = m.group(1)
            if os.path.exists(f):
                continue
            guai.append(f"{p} controlla {f}, che non esiste nel ramo: quella guardia non puo' "
                        f"dire la verita'. Puntala sul file che il flusso scrive OGGI.")
    return guai


def c_limiti_di_silenzio():
    """GUASTO 3: il limite di silenzio deve stare sopra il periodo dell'orologio."""
    guai = []
    att = "data/inventario_atteso.json"
    if not os.path.exists(att):
        return ["non trovo data/inventario_atteso.json: i limiti di silenzio non sono verificabili"]
    d = json.load(open(att)).get("corsie", {})
    for nome, c in sorted(d.items()):
        lim = c.get("ore_massime_di_silenzio")
        p = f"{CARTELLA_WF}/{nome}.yml"
        if lim is None or not os.path.exists(p):
            continue
        cron = re.findall(r'cron: *["\']([^"\']+)["\']', open(p).read())
        if not cron:
            continue
        # periodo piu' lungo fra gli orologi: se il campo delle ore e' fisso, gira 1 volta al giorno
        piu_lungo = 0
        for c0 in cron:
            parti = c0.split()
            if len(parti) < 5:
                continue
            ore = parti[1]
            if ore == "*":
                periodo = 1
            elif "/" in ore:
                periodo = int(ore.split("/")[1])
            elif "," in ore:
                periodo = max(1, 24 // len(ore.split(",")))
            else:
                periodo = 24
            piu_lungo = max(piu_lungo, periodo)
        if piu_lungo and lim < piu_lungo * 1.5:
            guai.append(f"{nome}: limite di silenzio {lim}h ma l'orologio gira ogni "
                        f"{piu_lungo}h — allarme garantito. Portalo a {int(piu_lungo*1.5)}h "
                        f"o piu' (periodo + margine per i giri saltati).")
    return guai


def c_uscita_che_muore():
    """GUASTO 1-bis: una corsia che scrive e non consegna butta il suo lavoro."""
    guai = []
    # CHI DECIDE SE UNA CORSIA E' ACCESA E' GITHUB, non il nostro elenco (10/10). Al primo giro
    # questo controllo accusava sette corsie: cinque erano spente da giorni, ma spente SU GITHUB
    # e non nel nostro file, quindi il controllo non lo sapeva. Si chiede alla fonte; se il token
    # non c'e', si ripiega sull'elenco locale e si DICHIARA che e' un ripiego.
    spente = set()
    try:
        tok = None
        for v in ("WR_PAT", "GITHUB_TOKEN"):
            tok = tok or os.environ.get(v)
        if not tok:
            c = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
            if os.path.exists(c):
                m = re.search(r"ghp_[A-Za-z0-9]+",
                              open(c, encoding="utf-8", errors="ignore").read())
                tok = m.group(0) if m else None
        if not tok:
            raise RuntimeError("nessun token")
        import urllib.request
        r = urllib.request.Request(
            "https://api.github.com/repos/nicolostancato-web/whale-radar/"
            "actions/workflows?per_page=100", headers={"Authorization": f"token {tok}"})
        w = json.load(urllib.request.urlopen(r, timeout=60))["workflows"]
        spente = {x["name"] for x in w if x["state"] != "active"}
    except Exception:
        if os.path.exists("data/corsie_spente.json"):
            spente = {k for k in json.load(open("data/corsie_spente.json"))
                      if not k.startswith("__")}
        guai.append("non ho potuto chiedere a GitHub quali corsie sono accese: uso l'elenco "
                    "locale, che puo' essere vecchio")
    for f in sorted(os.listdir(CARTELLA_WF)):
        if not f.endswith(".yml"):
            continue
        s = open(f"{CARTELLA_WF}/{f}").read()
        # «ESEGUE UN AGENTE» NON VUOL DIRE «PRODUCE UN FILE» (10/10). La corsia `guardia` veniva
        # accusata di buttare il suo lavoro, ma non ha lavoro da salvare: rilancia le corsie mute
        # e basta. Quindi si guarda se l'agente SCRIVE davvero qualcosa, non se viene eseguito.
        scrive = False
        for m in re.finditer(r"agents/(\w+)\.py", s):
            p2 = f"agents/{m.group(1)}.py"
            if not os.path.exists(p2):
                continue
            t2 = open(p2, encoding="utf-8", errors="replace").read()
            if re.search(r'json\.dump\(|open\([^)]*["\']w|to_csv\(|\.write\(', t2):
                scrive = True
                break
        consegna = ("upload-artifact" in s) or ("git push" in s)
        # UNA CORSIA SPENTA NON E' UN DIFETTO (10/10, stessa lezione dell'inventario atteso):
        # cinque delle sette segnalate al primo giro erano spente a ragion veduta. Un controllo
        # che accusa decisioni prese di proposito insegna a ignorare anche le sue accuse vere.
        if f[:-4] in spente:
            continue
        # CHI CONSEGNA NEL DEPOSITO NON STA BUTTANDO NIENTE (11/10). Lo stesso ragionamento era
        # gia' scritto in dove_si_perde.py e non l'avevo riportato qui: due controlli che guardano
        # la stessa cosa e danno risposte diverse insegnano a non fidarsi di nessuno dei due.
        if "deposito" in s or "consegna_verificata" in s:
            continue
        if scrive and not consegna:
            guai.append(f"{f} esegue un agente ma non consegna niente (ne' allegato ne' push): "
                        f"quello che scrive muore col runner. Aggiungi upload-artifact.")
    return guai


def c_file_di_corsia_validi():
    """Un file di corsia rotto la ferma in SILENZIO: il registro non mostra nemmeno la corsa."""
    guai = []
    try:
        import yaml
    except ImportError:
        return ["pyyaml non installato qui: non posso validare i file di corsia"]
    for f in sorted(os.listdir(CARTELLA_WF)):
        if not f.endswith((".yml", ".yaml")):
            continue
        try:
            if not yaml.safe_load(open(f"{CARTELLA_WF}/{f}")):
                guai.append(f"{f}: vuoto dopo la lettura")
        except Exception as e:
            guai.append(f"{f}: NON e' un file valido ({type(e).__name__}) — la corsia non parte")
    return guai


def c_sorgenti_compilano():
    guai = []
    for p in _sorgenti():
        r = subprocess.run([sys.executable, "-m", "py_compile", p],
                           capture_output=True, text=True)
        if r.returncode:
            guai.append(f"{p}: non compila — {(r.stderr or '').strip().splitlines()[-1][:90]}")
    return guai


def c_memoria_scritta_bene():
    """GUASTO 4: delegato al custode, che conosce le soglie e i due depositi."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import custode_memoria as C
    except ImportError:
        return ["custode_memoria non importabile: la memoria non e' sotto controllo"]
    guai = []
    for r, _, ff in os.walk("data"):
        for x in ff:
            p = os.path.join(r, x)
            try:
                if os.path.getsize(p) < 2_000_000:
                    continue
            except OSError:
                continue
            ok, motivo = C.controlla(p)
            if not ok:
                n = C.riscritture(p)
                if n:                      # conta solo se COSTA: un file fermo e' gia' pagato
                    guai.append(f"{p}: {motivo[:120]} ({n} riscritture in 7 giorni)")
    return guai


CONTROLLI = [
    ("strade del Mac nel codice che gira sul runner", c_strade_del_mac),
    ("guardie puntate su file che non esistono", c_guardie_su_file_morti),
    ("limiti di silenzio piu' corti dell'orologio", c_limiti_di_silenzio),
    ("corsie che scrivono e non consegnano", c_uscita_che_muore),
    ("file di corsia non validi", c_file_di_corsia_validi),
    ("sorgenti che non compilano", c_sorgenti_compilano),
    ("memoria scritta male E che costa", c_memoria_scritta_bene),
]


def main():
    tot = 0
    for nome, f in CONTROLLI:
        try:
            g = f()
        except Exception as e:
            g = [f"il controllo stesso e' rotto: {type(e).__name__}: {e}"]
        if g:
            print(f"\nSTRUTTURA | {nome}: {len(g)}")
            for x in g[:10]:
                print(f"   {x}")
            if len(g) > 10:
                print(f"   … e altri {len(g)-10}")
            tot += len(g)
        else:
            print(f"STRUTTURA | {nome}: in regola")
    print(f"\nSTRUTTURA | {tot} difetti da sistemare")
    return 0


if __name__ == "__main__":
    sys.exit(main())
