"""Le caratteristiche vere di un pool al momento della decisione.

PERCHE' ESISTE (23/09 notte, dopo una critica giusta del fondatore).
Fino a stasera il loop 1 sceglieva fra CINQUE numeri grezzi: quanti compratori, quanti scambi, il
ritmo, il rapporto fra i due, l'eta'. Con quei cinque ho trovato una regola a due soglie — «11
compratori e 73 scambi» — che e' il livello di analisi di un foglio di calcolo.

Il difetto non era usare due condizioni: era avere solo cinque numeri fra cui scegliere. Ho affamato
il modello e poi mi sono lamentato che fosse semplice.

Qui si estrae tutto cio' che i dati contengono davvero. Ogni scambio porta: portafoglio, importo CON
SEGNO (quindi si sa chi compra e chi vende), blocco, posizione dentro il blocco, dex. Da questo si
ricavano pressione, concentrazione, accelerazione, struttura dei partecipanti, forma del prezzo.

REGOLA NON NEGOZIABILE: ogni caratteristica usa SOLO cio' che e' noto entro t_decisione.
Nessuna guarda avanti. E' l'errore che Astra ha trovato stanotte e che ho poi rifatto nella prova in
avanti: qui si paga una volta sola, con una funzione che riceve gia' tagliati gli scambi.
"""
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verso as _V                                                # noqa: E402


def _gini(v):
    """Quanto e' concentrato: 0 = tutti uguali, 1 = uno solo ha tutto."""
    v = sorted(x for x in v if x > 0)
    if len(v) < 2:
        return 0.0
    n = len(v)
    tot = sum(v)
    if tot <= 0:
        return 0.0
    cum = sum((i + 1) * x for i, x in enumerate(v))
    return (2 * cum) / (n * tot) - (n + 1) / n


def _sicuro(f, default=0.0):
    try:
        v = f()
        if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
            return default
        return v
    except Exception:
        return default


# GLI ATTRIBUTI CHE ESISTONO ANCHE A DUE SCAMBI (2/10). Scoperto stanotte chiedendo un insieme
# a ingresso 2: tornava sempre vuoto, perche' qui c'era `if len(prima) < 5: return None`.
# Entrare prima NON e' un cambio di parametro — gli attributi stessi vogliono cinque scambi:
# una mediana su due numeri, «quota dei primi tre» su due scambi, le due meta' del periodo,
# sono conti che restituiscono numeri senza significare niente.
# E questo indica la strada: **l'attributo insider ha bisogno di UN solo scambio**, perche' chi
# ha comprato per primo si sa subito. La microstruttura no. Quindi una strategia precoce poggia
# sulle persone, non sulla microstruttura.
# Qui sotto l'elenco di cio' che a due scambi significa ancora qualcosa. Gli altri NON vengono
# emessi: un attributo assente si vede, uno degenere somiglia a una misura.
PRECOCI = ("scambi", "eta_ore", "quota_acquisti", "pressione_numero", "impatto_tipico",
           "pers_copertura", "pers_distinte", "pers_scambi_per", "pers_gini",
           "pers_quota_prima", "pers_solo_compra", "pers_nuove_dopo")


def estrai(prima, prezzo, persone=None, minimo=5, meme_t0=None):
    """`prima` = SOLO gli scambi fino al momento della decisione, ordinati per tempo.

    `prezzo(scambio)` -> prezzo o None. Torna un dizionario di caratteristiche.

    `persone` = mappa hash della transazione -> chi ha FIRMATO davvero (minuscole), oppure None.

    PERCHE' SERVE (1/10). Tutti gli attributi sui partecipanti qui sotto usano il campo `w`
    dello scambio. Il 25/09 abbiamo misurato che quel campo e' il ROUTER nell'81% dei casi — un
    solo indirizzo faceva il 42,6% degli scambi, cosa che nessun trader fa. Quindi
    «compratori», «scambi per portafoglio», «gini portafogli», «quota primo portafoglio» e
    «quota portafogli nuovi dopo» misurano PORTE, non gente.
    La correzione (`agents/iniziatori.py`) esiste dal 25/09 e non e' mai arrivata qui: la
    ricerca ha girato sei giorni sugli attributi sbagliati.
    IN POSITIVO: gli stessi conti si rifanno sulle PERSONE e si aggiungono come attributi
    nuovi, con il prefisso `pers_`. I vecchi restano — non si cancella niente — cosi' la
    ricerca giudica da sola quali dei due valgono, invece di crederlo io.
    """
    if len(prima) < max(2, minimo):
        return None
    t0, t1 = prima[0]["ts"], prima[-1]["ts"]
    durata = max(60.0, t1 - t0)
    c = {}

    # --- importi con segno: chi compra e chi vende ---
    # DUE DIFETTI NELLO STESSO POSTO, ENTRAMBI MISURATI IL 5/10.
    #
    # (1) QUALE LATO E' IL MEMECOIN VARIA, E QUI ERA FISSO. La regola era «a0 < 0 = acquisto»,
    #     che presuppone che il memecoin sia sempre il lato 0. Misurato: il memecoin sta sul
    #     lato 1 nel 67,2% delle coppie su base e nel 78,3% su robinhood. Quindi la
    #     classificazione era rovesciata su due terzi dei pool — e tutto il resto del codice
    #     passa `meme_t0` esplicitamente, quindi era solo questo file a indovinare.
    #
    # (2) IL V4 HA I SEGNI ROVESCIATI (vedi verso.py): nei V4 gli importi sono dalla
    #     prospettiva di chi scambia, non della pool. Verificato sulla chain, dieci casi su
    #     dieci, cinque per verso.
    #
    # E I DUE SI COMBINANO: un pool V4 col memecoin sul lato 1 veniva invertito DUE volte,
    # quindi risultava corretto per caso. E' questo che produceva l'asimmetria fra le due
    # famiglie di pool che ho misurato stamattina e non riuscivo a spiegare.
    #
    # LA CURA E' UNA SOLA: chiamare la funzione di riferimento `verso.e_vendita`, che sa del
    # lato e sa del V4. Scrivere qui una terza versione della stessa logica e' esattamente
    # come sono nati i due difetti.
    if meme_t0 is None:
        raise ValueError(
            "caratteristiche.estrai: serve meme_t0 (quale lato e' il memecoin). "
            "Senza, compra e vende si invertono sul 67-78% dei pool: misurato il 5/10. "
            "Non metto un valore di ripiego, perche' un ripiego silenzioso e' come e' nato "
            "questo difetto.")
    acquisti, vendite = [], []
    per_w = {}
    for x in prima:
        try:
            a1 = abs(float(x["a1" if meme_t0 else "a0"]))   # la VALUTA, non il gettone
        except Exception:
            continue
        if a1 <= 0:
            continue
        vende = _V.e_vendita(x, meme_t0)
        (vendite if vende else acquisti).append(a1)
        w = str(x.get("w", "")).lower()
        d = per_w.setdefault(w, {"n": 0, "compra": 0.0, "vende": 0.0, "primo": x["ts"]})
        d["n"] += 1
        d["vende" if vende else "compra"] += a1
    tutti = acquisti + vendite
    # lo stesso minimo anche qui: c'erano DUE soglie a cinque, e correggerne una sola
    # lasciava il difetto intatto. Un controllo doppio si corregge due volte.
    if len(tutti) < max(2, minimo) or not per_w:
        return None
    va, vv = sum(acquisti), sum(vendite)
    vtot = va + vv

    # --- PRESSIONE: quanto pesa il lato acquisto, in volume e in numero ---
    c["pressione_volume"] = _sicuro(lambda: (va - vv) / vtot)
    c["pressione_numero"] = _sicuro(lambda: (len(acquisti) - len(vendite)) / len(tutti))
    c["quota_acquisti"] = _sicuro(lambda: len(acquisti) / len(tutti))

    # la pressione sta CRESCENDO o calando? (prima meta' contro seconda meta' del tempo)
    meta = t0 + (t1 - t0) / 2
    p1 = [x for x in prima if x["ts"] <= meta]
    p2 = [x for x in prima if x["ts"] > meta]

    def press(g):
        # SECONDO DEI TRE PUNTI con la stessa regola fissa (5/10): correggerne uno solo
        # lascia il difetto intatto negli altri due, ed e' la lezione «un controllo doppio si
        # corregge due volte» — qui vale per tre.
        a = s = 0.0
        for x in g:
            try:
                a1 = abs(float(x["a1" if meme_t0 else "a0"]))
            except Exception:
                continue
            if a1 <= 0:
                continue
            if _V.e_vendita(x, meme_t0):
                s += a1
            else:
                a += a1
        return (a - s) / (a + s) if (a + s) > 0 else 0.0
    c["pressione_delta"] = _sicuro(lambda: press(p2) - press(p1))
    c["ritmo_delta"] = _sicuro(lambda: (len(p2) - len(p1)) / max(1, len(prima)))

    # --- DIMENSIONI: chi muove davvero il mercato ---
    tutti_ord = sorted(tutti, reverse=True)
    c["gini_importi"] = _sicuro(lambda: _gini(tutti))
    c["quota_primo_scambio"] = _sicuro(lambda: tutti_ord[0] / vtot)
    c["quota_primi_tre"] = _sicuro(lambda: sum(tutti_ord[:3]) / vtot)
    med = statistics.median(tutti)
    c["rapporto_max_mediano"] = _sicuro(lambda: tutti_ord[0] / med)
    c["quota_scambi_piccoli"] = _sicuro(
        lambda: sum(1 for x in tutti if x < med / 4) / len(tutti))

    # --- PARTECIPANTI: quanti, quanto concentrati, chi accumula ---
    n_w = len(per_w)
    c["compratori"] = n_w
    c["scambi"] = len(prima)
    c["scambi_per_portafoglio"] = _sicuro(lambda: len(prima) / n_w)
    volumi_w = [d["compra"] + d["vende"] for d in per_w.values()]
    c["gini_portafogli"] = _sicuro(lambda: _gini(volumi_w))
    c["quota_primo_portafoglio"] = _sicuro(lambda: max(volumi_w) / sum(volumi_w))
    c["quota_solo_un_scambio"] = _sicuro(
        lambda: sum(1 for d in per_w.values() if d["n"] == 1) / n_w)
    # chi ha sia comprato sia venduto: sta girando, non accumulando
    c["quota_girano"] = _sicuro(
        lambda: sum(1 for d in per_w.values() if d["compra"] > 0 and d["vende"] > 0) / n_w)
    c["quota_solo_compra"] = _sicuro(
        lambda: sum(1 for d in per_w.values() if d["compra"] > 0 and d["vende"] == 0) / n_w)
    # quanti portafogli NUOVI compaiono nella seconda meta': la folla sta arrivando o e' finita?
    visti1 = {str(x.get("w", "")).lower() for x in p1}
    nuovi2 = {str(x.get("w", "")).lower() for x in p2} - visti1
    c["quota_portafogli_nuovi_dopo"] = _sicuro(lambda: len(nuovi2) / n_w)

    # --- LE STESSE COSE, MA SULLE PERSONE (1/10) ---
    # `pers_copertura` dice su quanta parte degli scambi conosciamo la persona: senza quel
    # numero, «due persone distinte» puo' voler dire «ce n'erano due» oppure «ne conosciamo due
    # su venti». Un attributo senza la sua copertura e' un numero che mente con educazione.
    if persone:
        per_p, risolti = {}, 0
        for x in prima:
            # TERZO DEI TRE PUNTI con la stessa regola fissa (5/10).
            try:
                a1 = abs(float(x["a1" if meme_t0 else "a0"]))
            except Exception:
                continue
            if a1 <= 0:
                continue
            chi = persone.get(str(x.get("tx", "")).lower())
            if not chi:
                continue
            risolti += 1
            d = per_p.setdefault(chi, {"n": 0, "compra": 0.0, "vende": 0.0, "primo": x["ts"]})
            d["n"] += 1
            d["vende" if _V.e_vendita(x, meme_t0) else "compra"] += a1
        c["pers_copertura"] = _sicuro(lambda: risolti / len(prima))
        n_p = len(per_p)
        c["pers_distinte"] = n_p
        if n_p:
            vol_p = [d["compra"] + d["vende"] for d in per_p.values()]
            c["pers_scambi_per"] = _sicuro(lambda: risolti / n_p)
            c["pers_gini"] = _sicuro(lambda: _gini(vol_p))
            c["pers_quota_prima"] = _sicuro(lambda: max(vol_p) / sum(vol_p))
            c["pers_solo_compra"] = _sicuro(
                lambda: sum(1 for d in per_p.values() if d["compra"] > 0 and d["vende"] == 0) / n_p)
            meta = prima[len(prima) // 2]["ts"]
            c["pers_nuove_dopo"] = _sicuro(
                lambda: sum(1 for d in per_p.values() if d["primo"] > meta) / n_p)
        else:
            for k in ("pers_scambi_per", "pers_gini", "pers_quota_prima",
                      "pers_solo_compra", "pers_nuove_dopo"):
                c[k] = 0.0

    # --- TEMPO: ritmo, accelerazione, buchi ---
    gap = [b["ts"] - a["ts"] for a, b in zip(prima, prima[1:])]
    gap_pos = [g for g in gap if g > 0]
    c["ritmo_ora"] = _sicuro(lambda: len(prima) / (durata / 3600))
    c["gap_mediano"] = _sicuro(lambda: statistics.median(gap_pos)) if gap_pos else 0.0
    c["gap_massimo"] = _sicuro(lambda: max(gap)) if gap else 0.0
    c["irregolarita_tempi"] = _sicuro(
        lambda: statistics.pstdev(gap_pos) / statistics.mean(gap_pos)) if len(gap_pos) > 2 else 0.0
    # quanti scambi nello STESSO blocco: e' attivita' automatica, non gente
    blocchi = [x.get("blocco") for x in prima if x.get("blocco") is not None]
    c["quota_stesso_blocco"] = _sicuro(
        lambda: 1 - len(set(blocchi)) / len(blocchi)) if blocchi else 0.0

    # --- PREZZO: forma del percorso, non solo il punto di arrivo ---
    pp = [(x["ts"], prezzo(x)) for x in prima]
    pp = [(t, p) for t, p in pp if p and p > 0]
    if len(pp) >= 5:
        val = [p for _, p in pp]
        c["rendimento_finora"] = _sicuro(lambda: val[-1] / val[0] - 1)
        c["massimo_finora"] = _sicuro(lambda: max(val) / val[0] - 1)
        c["caduta_dal_massimo"] = _sicuro(lambda: val[-1] / max(val) - 1)
        salti = [b / a - 1 for a, b in zip(val, val[1:]) if a > 0]
        c["volatilita"] = _sicuro(lambda: statistics.pstdev(salti)) if len(salti) > 2 else 0.0
        c["quota_salite"] = _sicuro(lambda: sum(1 for s in salti if s > 0) / len(salti))
        c["impatto_tipico"] = _sicuro(
            lambda: statistics.median([abs(s) for s in salti])) if salti else 0.0
        # il prezzo finale sta sopra o sotto la media dei prezzi pagati?
        c["sopra_la_media"] = _sicuro(lambda: val[-1] / statistics.mean(val) - 1)
    else:
        for k in ("rendimento_finora", "massimo_finora", "caduta_dal_massimo", "volatilita",
                  "quota_salite", "impatto_tipico", "sopra_la_media"):
            c[k] = 0.0

    # --- STRUTTURA ---
    c["dex_diversi"] = len({x.get("dex") for x in prima if x.get("dex") is not None})
    c["eta_ore"] = durata / 3600
    if minimo < 5:
        # ingresso precoce: si emettono SOLO gli attributi che a due scambi significano qualcosa
        c = {k: v for k, v in c.items() if k in PRECOCI}
    return c


NOMI = None


def nomi(esempio):
    """L'ordine delle colonne, stabile: un modello addestrato ieri deve leggere le stesse."""
    return sorted(esempio.keys())
