"""IL BANCO DEGLI INCIDENTI VERI — «il sistema di oggi avrebbe pescato quel guasto?»

PERCHE' ESISTE (28/09). Abbiamo un banco di prova (`prova_metro.py`) che controlla sei casi scelti
DA ME conoscendo l'implementazione. E' utile, ma ha un difetto strutturale: **chi scrive il test e
chi scrive il codice sono la stessa persona**, quindi il codice passa per costruzione. E' la
definizione dello studente che ha visto le domande prima dell'esame.

Qui invece i casi NON li ho scelti io: **sono guasti realmente accaduti**, ognuno costato ore o
giorni, tutti avvenuti PRIMA che esistessero le difese che oggi dovrebbero fermarli.
La domanda che pone questo file e' la sola che smaschera il teatro:

    *«il sistema di oggi, messo davanti a quel caso, se ne accorgerebbe?»*

Se un controllo costruito per impedire un errore non riconosce l'errore storico che dice di
prevenire, **non e' una difesa: e' una decorazione**, e va buttata.

DIFFERENZA IMPORTANTE DA `prova_metro.py`: qui non si chiamano le funzioncine singole, si fa girare
**il vero `insieme.py`** su dati costruiti come quelli veri. Un test che riscrive le formule
verifica la mia copia, non il sistema — era il rilievo giusto della revisione del 28/09.
"""
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

QUI = os.path.dirname(os.path.abspath(__file__))
ESITI = []

# indirizzi finti ma con la proprieta' che conta: la "valuta" compare in molti pool, il memecoin no
VALUTA = "0x5555000000000000000000000000000000000001"


def _meme(nome, alto=True):
    """Un indirizzo diverso per ogni pool.

    OGNI POOL IL SUO MEMECOIN: se lo stesso indirizzo compare in due pool, con la soglia di prova
    abbassata `verso.py` lo scambia per una VALUTA (compare in piu' pool = e' un hub) e salta tutto.
    La prova ha accusato il sistema per questo, ed era colpa sua.
    `alto=True` -> indirizzo maggiore della valuta, quindi il memecoin e' token1.
    """
    h = abs(hash(nome)) % 10**8
    return ("0xbbbb" if alto else "0x1111") + f"{h:032d}"


def _scambio(ts, a0, a1, w="0x01", tx=None, li=0):
    return {"ts": ts, "a0": a0, "a1": a1, "w": w, "w_sem": "prova",
            "tx": tx or f"0x{ts}{li}", "li": li, "dex": 3, "blocco": ts}


def _scrivi_pool(base, nome, scambi):
    d = os.path.join(base, "data/multichain/prova/storico")
    os.makedirs(d, exist_ok=True)
    with gzip.open(os.path.join(d, f"{nome}.jsonl.gz"), "wt") as f:
        for s in scambi:
            f.write(json.dumps(s) + "\n")


def _gira_insieme(base, coppie):
    """Fa girare il VERO insieme.py sui dati costruiti. Torna le righe prodotte.

    DUE ACCORTEZZE, imparate facendo fallire la prova la prima volta.
    `verso.py` riconosce la valuta perche' compare in MOLTI pool (soglia 50): con due o tre pool di
    prova nessun token sembra una valuta, e `insieme` salta tutto dicendo «non si capisce quale
    token e' il memecoin». Quindi qui la soglia si abbassa a due e si aggiunge un pool di contorno
    che usa la stessa valuta.
    Non e' barare: la soglia e' un parametro dichiarato, e la LOGICA che si vuole mettere alla prova
    — come si riconosce il verso, come si misura l'uscita — resta quella vera.
    **Ma la prima volta la prova ha gridato tre guasti che erano suoi, non del sistema**, ed e'
    esattamente il falso allarme che fa disattivare i controlli: verificare prima di gridare.
    """
    os.makedirs(os.path.join(base, "data/multichain/prova"), exist_ok=True)
    coppie = dict(coppie)
    coppie["p_contorno"] = {"t0": VALUTA, "t1": _meme("p_contorno"), "dex": 3}
    ora = int(time.time()) - 6 * 86400
    _scrivi_pool(base, "p_contorno", [_scambio(ora + i * 60, a0=-5, a1=50, li=i) for i in range(8)])
    json.dump({"coppie": coppie}, open(os.path.join(base, "data/multichain/prova/coppie.json"), "w"))
    amb = dict(os.environ, CHAIN="prova", ORE_ATTESA="1", ORIZZONTE_ORE="24", SOGLIA_HUB="2",
               MIN_VITA="6", MIN_VENDITE="1", RITARDO_MINIMO_S="1", MIN_DOPO="1")
    r = subprocess.run([sys.executable, "-B", os.path.join(QUI, "insieme.py")],
                       cwd=base, env=amb, capture_output=True, text=True)
    p = os.path.join(base, "data/loop1/insieme_prova.jsonl.gz")
    if not os.path.exists(p):
        print("   (insieme non ha prodotto nulla)", r.stdout[-300:], r.stderr[-300:])
        return []
    return [json.loads(l) for l in gzip.open(p, "rt")]


def prova(nome, quando, ok, dettaglio=""):
    ESITI.append((ok, nome))
    print(f"   {'PESCATO ' if ok else 'SFUGGITO'} [{quando}] {nome} {dettaglio}")


# --------------------------------------------------------------------------------------
def incidente_verso(base):
    """26/09 — Contavamo gli ACQUISTI come vendite nel 73% dei pool.

    Il verso dipende dall'ordine alfabetico degli indirizzi: dove la valuta e' token0, `a0 > 0`
    vuol dire «entra valuta», cioe' qualcuno ha COMPRATO. Per giorni l'uscita e' stata misurata
    sui prezzi di chi entrava. Costo: due verdetti pubblicati e poi sospesi.
    """
    ora = int(time.time()) - 5 * 86400
    # valuta = token0 (indirizzo piu' basso), memecoin = token1
    # ATTENZIONE AL VERSO ANCHE QUI: il memecoin e' token1, quindi una VENDITA e' memecoin che
    # ENTRA nel pool (a1 > 0) e valuta che ESCE (a0 < 0). Scrivendoli al contrario la prima volta,
    # la prova ha accusato il sistema di un guasto che era suo.
    s = [_scambio(ora + i, a0=100, a1=-1000, li=i) for i in range(8)]           # ACQUISTI (prima)
    s += [_scambio(ora + 3700 + i, a0=-200, a1=1000, li=i) for i in range(6)]   # VENDITE (dopo)
    s += [_scambio(ora + 4200 + i, a0=150, a1=-1000, li=20 + i) for i in range(3)]  # ACQUISTI (dopo)
    _scrivi_pool(base, "p_verso", s)
    righe = _gira_insieme(base, {"p_verso": {"t0": VALUTA, "t1": _meme("p_verso"), "dex": 3}})
    r = next((x for x in righe if x["_pool"] == "p_verso"), None)
    if not r:
        return prova("verso: acquisti contati come vendite", "26/09", False, "(pool non prodotto)")
    # DOPO il momento della decisione ci sono 5 vendite e 3 acquisti.
    # Cinque e non sei perche' la prima vendita E' lo scambio d'ingresso, e l'ingresso non fa parte
    # del «dopo»: l'ho scoperto qui, e lo lascio scritto invece di aggiustare il numero per far
    # passare la prova — **un test che si adatta al risultato non prova piu' niente.**
    # Col codice sbagliato (`a0 > 0` = vendita, mentre qui il memecoin e' token1) ne conterebbe 3.
    prova("verso: acquisti contati come vendite", "26/09",
          r["_vendite_dopo"] == 5,
          f"(contate {r['_vendite_dopo']}; giuste 5, col difetto sarebbero 3)")


def incidente_finestra(base):
    """25/09 mattina — Misuravamo esiti a 24 ore su pool osservati poche ore.

    Chi non aveva vendite PERCHE' NON AVEVAMO GUARDATO finiva fra le trappole: il tasso risultava
    35% invece del vero. Costo: sei giorni di numeri gonfi del doppio.
    """
    ora = int(time.time()) - 5 * 86400
    # un pool vecchio (fissa la frontiera della raccolta) e uno nato DUE ORE prima della fine
    vecchio = [_scambio(ora + i * 600, a0=-10, a1=100, li=i) for i in range(10)]
    vecchio += [_scambio(ora + 4 * 86400 + i, a0=10, a1=-100, li=i) for i in range(6)]
    giovane = [_scambio(ora + 4 * 86400 - 7200 + i * 60, a0=-10, a1=100, li=i) for i in range(10)]
    _scrivi_pool(base, "p_vecchio", vecchio)
    _scrivi_pool(base, "p_giovane", giovane)
    righe = _gira_insieme(base, {"p_vecchio": {"t0": VALUTA, "t1": _meme("p_vecchio"), "dex": 3},
                                 "p_giovane": {"t0": VALUTA, "t1": _meme("p_giovane"), "dex": 3}})
    g = next((x for x in righe if x["_pool"] == "p_giovane"), None)
    prova("finestra: pool troppo giovane giudicato a 24 ore", "25/09",
          g is None or not g.get("_giudicabile"),
          f"(giudicabile: {g.get('_giudicabile') if g else 'assente'})")


def incidente_sopravvivenza(base):
    """25/09 sera — La correzione della mattina era peggio del difetto.

    «Giudicabile = abbiamo visto 24 ore di scambi su questo pool» toglieva i pool MORTI, cioe'
    proprio le trappole: il tasso scendeva di sette punti per pura sopravvivenza.
    Un pool morto in dieci minuti ma NATO giorni fa deve restare giudicabile.
    """
    ora = int(time.time()) - 5 * 86400
    vecchio = [_scambio(ora + i * 600, a0=-10, a1=100, li=i) for i in range(10)]
    vecchio += [_scambio(ora + 4 * 86400 + i, a0=10, a1=-100, li=i) for i in range(6)]
    # DEVE MORIRE DOPO IL MOMENTO IN CUI SI COMPRA, non prima: un pool spento in dieci minuti non
    # e' una trappola in cui si cade, e' un pool in cui non si entra mai — e infatti il sistema lo
    # scarta, giustamente. L'incidente vero riguardava i pool che scambiano per un po', ti fanno
    # entrare, e poi si spengono prima dell'orizzonte.
    morto = [_scambio(ora + i * 600, a0=100, a1=-1000, li=i) for i in range(12)]   # due ore di vita
    morto += [_scambio(ora + 7300, a0=-50, a1=1000, li=99)]                        # una vendita sola
    # ...e poi piu' niente per giorni
    _scrivi_pool(base, "p_vecchio", vecchio)
    _scrivi_pool(base, "p_morto", morto)
    righe = _gira_insieme(base, {"p_vecchio": {"t0": VALUTA, "t1": _meme("p_vecchio"), "dex": 3},
                                 "p_morto": {"t0": VALUTA, "t1": _meme("p_morto"), "dex": 3}})
    m = next((x for x in righe if x["_pool"] == "p_morto"), None)
    prova("sopravvivenza: il pool morto subito viene escluso", "25/09",
          m is not None and m.get("_giudicabile") is True,
          f"(giudicabile: {m.get('_giudicabile') if m else 'ASSENTE — escluso!'})")


def incidente_taglia(base):
    """26/09 notte — Un 10x che scambiava trentadue dollari sembrava un'uscita vera.

    L'ipotesi H6b dava +11% e regge va a tutti i controlli statistici. E' morta quando abbiamo
    misurato QUANTI SOLDI passavano a quei prezzi: mediana 32 dollari.
    L'uscita pesata per il denaro deve dare il prezzo vero, non la stampa da polvere.
    """
    ora = int(time.time()) - 5 * 86400
    s = [_scambio(ora + i * 600, a0=-100, a1=1000, li=i) for i in range(10)]
    # vendite grosse a prezzo 0,1 (valuta 100 per volta)
    s += [_scambio(ora + 4000 + i, a0=100, a1=-1000, li=i) for i in range(6)]
    # UNA stampa a 10x con polvere: valuta 1 sola
    s += [_scambio(ora + 5000, a0=1, a1=-1, li=99)]
    _scrivi_pool(base, "p_taglia", s)
    righe = _gira_insieme(base, {"p_taglia": {"t0": VALUTA, "t1": _meme("p_taglia"), "dex": 3}})
    r = next((x for x in righe if x["_pool"] == "p_taglia"), None)
    if not r or "_uscita_pesata" not in r:
        return prova("taglia: il 10x da polvere passa per uscita", "26/09", False,
                     "(manca _uscita_pesata)")
    # l'uscita pesata deve stare vicino al prezzo vero, non al 10x
    prova("taglia: il 10x da polvere passa per uscita", "26/09",
          r["_uscita_pesata"] < 1.0,
          f"(uscita pesata: {r['_uscita_pesata']:+.2f}, la stampa valeva +900%)")


def incidente_futuro(base):
    """27 e 28/09 — Condizionare su un campo che si conosce solo DOPO aver comprato.

    Due volte in due giorni: «i pool con volume alto rendono +24,9%» e poi «il fondale e' +15,0%
    per i pool capienti». Tutte e due false allo stesso modo — il volume e la capienza uscita si
    conoscono dopo l'entrata. Col dato visto PRIMA il fondale e' -12,1%: ventisette punti.
    La difesa non e' ricordarsene: e' che il dato si rifiuti.
    """
    import dati as D
    # SI COSTRUISCE IL PROPRIO CASO (1/10). Questa prova leggeva il dato di PRODUZIONE: dalla
    # copia leggera, dove i dati non ci sono, diceva «nessun dato da controllare» e risultava
    # SFUGGITA — cioe' il banco dichiarava scoperto un guasto che invece e' coperto.
    # Un controllo che ha bisogno dei dati veri non e' un controllo: e' un'ispezione, e tace
    # appena cambia l'ambiente. Gli altri quattro casi si costruiscono il loro: anche questo.
    import gzip as _gz
    import json as _js
    finto = os.path.join(base, "data", "loop1")
    os.makedirs(finto, exist_ok=True)
    with _gz.open(os.path.join(finto, "insieme_robinhood.jsonl.gz"), "wt") as h:
        # LE DATE DEVONO SODDISFARE IL FILTRO DI GIUDICABILITA' (1/10): `dati.carica` chiede
        # che il pool sia nato almeno un orizzonte prima della fine della raccolta. Con tutte
        # le righe nello stesso istante, scartava tutto e la prova risultava rotta.
        for i in range(3):
            h.write(_js.dumps({"_pool": f"0x{i:040x}",
                               "_t": 1790000000 + i,
                               "_ore_osservate": 200.0,
                               "_giudicabile": True, "_valuta_prima": 1.0,
                               "_valuta_venduta": 10.0, "_uscita": 0.1}) + "\n")
    _vecchia = os.getcwd()
    os.chdir(base)
    try:
        r = D.carica("robinhood")
    finally:
        os.chdir(_vecchia)
    if not r:
        return prova("futuro: si puo' filtrare su un campo dell'esito", "28/09", False,
                     "(il dato finto non si carica: la prova e' rotta, non il sistema)")
    try:
        _ = [x for x in r[:5] if x["_valuta_venduta"] > 0]
        prova("futuro: si puo' filtrare su un campo dell'esito", "28/09", False,
              "(il filtro e' passato senza protestare)")
    except KeyError:
        prova("futuro: si puo' filtrare su un campo dell'esito", "28/09", True,
              "(il dato si e' rifiutato)")


def main():
    print("INCIDENTI | guasti veri, gia' accaduti: il sistema di oggi se ne accorge?\n")
    for f in (incidente_verso, incidente_finestra, incidente_sopravvivenza,
              incidente_taglia, incidente_futuro):
        base = tempfile.mkdtemp(prefix="incidente_")
        try:
            f(base)
        except Exception as e:
            prova(f.__name__, "?", False, f"(la prova stessa e' esplosa: {type(e).__name__} {e})")
        finally:
            shutil.rmtree(base, ignore_errors=True)
    sfuggiti = [n for ok, n in ESITI if not ok]
    print()
    if sfuggiti:
        print(f"INCIDENTI | {len(sfuggiti)} guasti storici SFUGGONO al sistema di oggi:")
        for n in sfuggiti:
            print("   -", n)
        print("\nUna difesa che non riconosce l'errore che dice di prevenire e' una decorazione.")
        return 1
    print(f"INCIDENTI | tutti i {len(ESITI)} guasti storici verrebbero pescati.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
