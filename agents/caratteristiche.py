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
import statistics


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


def estrai(prima, prezzo):
    """`prima` = SOLO gli scambi fino al momento della decisione, ordinati per tempo.

    `prezzo(scambio)` -> prezzo o None. Torna un dizionario di caratteristiche.
    """
    if len(prima) < 5:
        return None
    t0, t1 = prima[0]["ts"], prima[-1]["ts"]
    durata = max(60.0, t1 - t0)
    c = {}

    # --- importi con segno: chi compra e chi vende ---
    acquisti, vendite = [], []
    per_w = {}
    for x in prima:
        try:
            a0 = float(x["a0"])
            a1 = abs(float(x["a1"]))
        except Exception:
            continue
        if a1 <= 0:
            continue
        (acquisti if a0 < 0 else vendite).append(a1)
        w = str(x.get("w", "")).lower()
        d = per_w.setdefault(w, {"n": 0, "compra": 0.0, "vende": 0.0, "primo": x["ts"]})
        d["n"] += 1
        d["compra" if a0 < 0 else "vende"] += a1
    tutti = acquisti + vendite
    if len(tutti) < 5 or not per_w:
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
        a = s = 0.0
        for x in g:
            try:
                a0 = float(x["a0"])
                a1 = abs(float(x["a1"]))
            except Exception:
                continue
            if a0 < 0:
                a += a1
            else:
                s += a1
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
    return c


NOMI = None


def nomi(esempio):
    """L'ordine delle colonne, stabile: un modello addestrato ieri deve leggere le stesse."""
    return sorted(esempio.keys())
