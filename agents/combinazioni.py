"""Cerca STRATEGIE fatte di condizioni incrociate, non manopole singole.

PERCHE' ESISTE (30/09). Decisione di Nicolo' del 23/09, che avevo perso per sette giorni:

  «Io mi aspetto una strategia mostruosa, dove si analizzano migliaia di combinazioni tutte
  perfette. Entriamo quando la pressione e' X%, poi si concatena con una percentuale costi
  cosi', oppure una percentuale di buyer che subentra in base alla liquidita', e poi si
  interseca questo settore. Una roba molto piu' complicata, tecnica, tutta fatta di parametri
  incrociati.»

Il 30/09 gli ho portato «compra al 5o scambio, $25, tieni una settimana»: UNA manopola.

LA TRAPPOLA DI QUESTO MESTIERE, E COME SI DISINNESCA.
Provando migliaia di combinazioni se ne trova SEMPRE una che sul passato sembra oro. Non e'
un rischio: e' una certezza matematica. Le tre difese, tutte obbligatorie:

  1. TRE PEZZI DI TEMPO, non due. Si cerca sul primo, si sceglie sul secondo, si giudica sul
     TERZO che non e' stato usato ne' per cercare ne' per scegliere.
  2. IL CONTROLLO SUL RUMORE. La stessa ricerca gira su esiti MESCOLATI, dove per costruzione
     non c'e' niente da trovare. Se la migliore sul vero non batte la migliore sul rumore,
     abbiamo trovato il rumore. Questo numero si stampa SEMPRE, anche quando e' scomodo.
  3. QUANTE NE HO PROVATE. Si dichiara. Una su mille che sembra buona, su mille provate, e'
     quello che ci si aspetta dal caso.

Le condizioni sono costruite solo su attributi noti PRIMA di comprare (nessun underscore):
e' il vincolo che agents/dati.py protegge da giorni.
"""
import gzip
import itertools
import json
import os
import sys

import numpy as np

MIN_POOL = 150          # sotto questo una combinazione non si giudica: e' aneddoto
MAX_CONDIZIONI = 3      # quante condizioni si incrociano al massimo
QUANTILI = (0.2, 0.5, 0.8)


COSTO = 0.018
RITARDO = int(os.environ.get("RITARDO", 1))   # scambi di latenza: 1 e' il minimo reale
# LA TAGLIA FA PARTE DELLA STRATEGIA (1/10): un vantaggio che esiste solo a $25 e muore a
# $100 non e' un vantaggio, e' una curiosita'. Misurato il 30/09: fra quelle due taglie
# ballano quindici punti di fondale.
SOLDI = float(os.environ.get("SOLDI", 25.0))


def esito_con_ritardo(x, soldi=None, ritardo=None):
    """L'esito comprando al prezzo OTTENIBILE, cioe' quello dello scambio successivo.

    IL PREZZO CHE VEDI NON E' QUELLO CHE PAGHI (30/09 notte). Il prezzo d'ingresso usato finora
    era quello dello scambio a cui entriamo: uno scambio avvenuto, ma non il nostro. Per comprare
    si manda una transazione, eseguita dopo quelle davanti.
    Misurato: con UN solo scambio di ritardo il fondale passa da +23,3% a −11,4% e la migliore
    combinazione da +207% a +0,9%. Cercare sul vecchio esito significa cercare l'irraggiungibile.
    """
    r = RITARDO if ritardo is None else ritardo
    soldi = SOLDI if soldi is None else soldi
    cam = x.get("_cammino") or []
    if len(cam) <= r:
        return None
    if r == 0:
        # IL SEGNAPOSTO CHE SEMBRAVA UN PREZZO (1/10). Qui c'era `p = 1.0 if r == 0`: con
        # ritardo 0 non si divideva per un prezzo ma per UNO, e usciva un numero plausibile —
        # media +28,6% — che non era un rendimento, erano dollari diviso uno.
        # Su quel numero era costruito il titolo del 30/09: «con un solo scambio di ritardo il
        # fondale passa da +23,3% a -11,4%». Il «prima» non era un fondale.
        # Misurato a mano l'1/10, senza segnaposto: comprare al prezzo dello scambio su cui si
        # decide da' -5,0% medio, comprare a quello SUCCESSIVO da' -6,9%. La latenza costa DUE
        # punti, non trentacinque.
        # IN POSITIVO: un argomento che non si puo' onorare si rifiuta ad alta voce. Il ritardo
        # si conta in scambi veri: 1 = il prezzo dello scambio su cui decido (che non posso
        # avere), 2 = il primo prezzo che posso davvero pagare.
        raise ValueError(
            "ritardo=0 non e' un prezzo: era il segnaposto 1.0, e un segnaposto che somiglia "
            "a un risultato ha prodotto il falso titolo del 30/09. Usa 1 (prezzo di decisione, "
            "non ottenibile) oppure 2 (primo prezzo ottenibile).")
    p = cam[r - 1][1]
    if p <= 0:
        return None
    riemp = inc = 0.0
    for _, pr, q in cam[r:]:
        if riemp >= soldi:
            break
        quota = min(q, soldi - riemp)
        riemp += quota
        inc += quota * (pr / p)
    if riemp <= 0:
        return -0.98
    u = inc / soldi - 1 - COSTO
    return max(-0.99, min(20.0, u))


def carica(chain, suffisso=None):
    """Carica l'insieme del momento d'ingresso chiesto, e URLA se non esiste.

    LA DIMENSIONE FANTASMA (1/10). Qui c'era `suffisso="_sc5"` scritto fisso, mentre il ciclo
    passava ENTRATA_SCAMBIO=5 e 25 come se fossero due esperimenti diversi. Non lo erano: le
    dodici prove con ingresso 25 hanno dato margini IDENTICI a quelle con ingresso 5
    (-12,1/-12,1, +5,5/+5,5, +3,4/+3,4). Meta' dello spazio di ricerca era un doppione contato
    come prova indipendente.

    E' `specification drift`: la configurazione dichiara una dimensione che il codice ignora.
    Non si e' visto per due giorni perche' il fallimento era SILENZIOSO — il programma girava,
    finiva, stampava un numero plausibile. Qui diventa rumoroso: se l'insieme del momento
    chiesto non c'e', si esce con errore. Un dato che non esiste non deve poter diventare una
    misura che somiglia a un'altra.
    """
    if suffisso is None:
        suffisso = "_sc%s" % os.environ.get("ENTRATA_SCAMBIO", "5")
    p = f"data/loop1/insieme_{chain}{suffisso}.jsonl.gz"
    if not os.path.exists(p):
        raise SystemExit(
            f"COMBINAZIONI | manca {p}: il momento d'ingresso "
            f"{os.environ.get('ENTRATA_SCAMBIO', '5')} non ha un insieme costruito. "
            f"NON ripiego sull'ingresso 5: ripiegare in silenzio e' come sono nate dodici "
            f"prove finte.")
    r = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
    # I POOL CHE SPARIVANO (1/10, dal punto cieco che ha nominato Grok).
    # «Mescolare gli esiti e tenere ferme le condizioni lascia in piedi il campione. Nel mazzo
    # ci sono soltanto le righe con uno scambio successivo archiviato. Passa una regola
    # correlata con "qui c'e' un print archiviato": vera nel file, ineseguibile sul mercato.»
    #
    # Qui `_bersaglio is None` veniva buttato via. Ma non e' un dato mancante: e' un ESITO.
    # Vuol dire che dopo il nostro acquisto non c'e' mai piu' stato uno scambio, cioe' che da
    # quella pool non si esce. Chi ci entra perde tutto. Buttarli via significava misurare il
    # mercato solo dove per caso qualcuno ha continuato a scambiare.
    # Misurato il 1/10: erano il 10,5% di robinhood e il 5,4% di base, e contarli sposta il
    # fondale da -6,3% a -16,1%. Dieci punti: piu' di ogni vantaggio mai trovato.
    # DUE STANDARD DI POOL, DUE POPOLAZIONI (1/10). L'id del pool ha due forme: 42 caratteri
    # (indirizzo di contratto) e 66 (id da 32 byte). Non e' un difetto dei dati: sono due
    # standard. Ma sono due popolazioni diverse — a pari scambi, 5 compratori mediani contro 2
    # su entrambe le chain — e su robinhood l'esito medio differisce di DODICI punti
    # (-23,1% contro -11,0%). E' noto prima di comprare e la ricerca era cieca, perche' `_pool`
    # e' privato. Il perche' dell'aggiunta sta in data/atomi_perche.json, come chiede la
    # decisione «atomi-congelati».
    for x in r:
        x["pool_a_indirizzo"] = 1 if len(str(x.get("_pool", ""))) <= 42 else 0
    giudicabili = [x for x in r if x.get("_giudicabile")]
    senza_cammino = [x for x in giudicabili if not x.get("_cammino")]
    r = [x for x in giudicabili if x.get("_cammino")]
    for x in r:
        e = esito_con_ritardo(x)
        # niente scambio successivo = non si esce mai = si perde tutto, meno la commissione
        x["_bersaglio"] = -1.0 if e is None else e
        x["_mai_uscito"] = e is None
    mai = sum(1 for x in r if x["_mai_uscito"])
    print(f"   mazzo: {len(r):,} pool, di cui {mai:,} da cui non si esce mai "
          f"(contati -100%, NON tolti); {len(senza_cammino):,} senza prezzo d'ingresso, "
          f"non entrabili", flush=True)
    r.sort(key=lambda x: x["_t"])

    # IL MERCATO ATTORNO, NON SOLO LA POOL (1/10). Fino a stasera ogni moneta veniva giudicata
    # da sola, come se fosse l'unica cosa al mondo: tutti e trentaquattro gli attributi
    # guardavano DENTRO la pool. Ma una moneta nata mentre la catena ribolle non e' la stessa
    # cosa di una nata nel deserto, e questo dato ce l'avevamo gia' — bastava incrociare quello
    # che possediamo e non abbiamo mai unito.
    # Misurato stasera, al prezzo pagabile: su robinhood il quinto piu' tranquillo rende -6,7%
    # contro -19,2% del quasi-piu'-affollato, dodici punti e mezzo. Su base la direzione si
    # INVERTE (il piu' tranquillo e' il peggiore, -29,4%): due chain, due comportamenti. Per
    # questo non e' un vantaggio da solo — ma e' una dimensione a cui la ricerca era cieca.
    # Si conta solo cio' che e' noto AL MOMENTO DELLA DECISIONE: quante altre decisioni cadono
    # nell'ora PRIMA di questa. Niente esiti di altre pool: quelli si sapranno solo dopo.
    # IL PASSATO DEI COMPRATORI, COME ATTRIBUTO (2/10). Misurato stanotte: ordinando per come
    # sono andate le monete PRECEDENTI dei primi compratori veri, il quinto peggiore fa -24%
    # (robinhood) e -48% (base), il migliore -0,3% e -3,7%. Lo scarto sopravvive a due attacchi:
    # pretendere che il passato sia CHIUSO da sei ore (il positivo iniziale era futuro) e usare
    # la storia dei compratori di un'altra moneta della stessa ora (una parte era il momento).
    # Restano 16 e 20 punti attribuibili alle PERSONE.
    # E non viene dal tempismo: lo stesso scarto a ingresso 5, 10 e 25 (+24/+18/+20 e +44/+57/+62).
    # Quindi non e' un segnale che trova i vincenti: e' un FILTRO che evita i disastri. Come
    # attributo serve a questo — restringere, e cercare il guadagno dentro cio' che resta.
    # LA REGOLA DELLE SEI ORE E' IL CUORE: una moneta precedente di dieci minuti prima ha un
    # esito che ANCORA NON SAPEVAMO. Usarla fa comparire un +16% che non esiste.
    percorso_ins = f"data/multichain/{chain}/insider.json.gz"
    if os.path.exists(percorso_ins):
        import collections
        try:
            primi = json.load(gzip.open(percorso_ins, "rt")).get("da", {})
        except Exception:
            primi = {}
        if primi:
            storia = collections.defaultdict(list)
            chiusura = float(os.environ.get("ORE_CHIUSURA", 6)) * 3600
            noti = 0
            for x in r:
                chi = primi.get(x.get("_pool")) or []
                lim = x["_t"] - chiusura
                pre = [[e for t, e in storia[w] if t <= lim] for w in chi]
                pre = [h for h in pre if h]
                if pre:
                    x["insider_storia"] = float(np.mean([np.mean(h) for h in pre]))
                    x["insider_quanti_noti"] = len(pre)
                    noti += 1
                else:
                    # NON si mette zero: zero vuol dire «andavano in pari», non «non lo sappiamo».
                    # Un valore finto in mezzo ai veri e' il segnaposto 1.0 di stamattina.
                    x["insider_storia"] = None
                    x["insider_quanti_noti"] = 0
                for w in chi:
                    storia[w].append((x["_t"], x["_bersaglio"]))
            print(f"   passato dei compratori noto per {noti:,} pool su {len(r):,} "
                  f"({100*noti/max(1,len(r)):.0f}%), chiuso da almeno "
                  f"{chiusura/3600:.0f} ore", flush=True)
            # le righe senza passato noto NON possono stare nello stesso mazzo di quelle con:
            # un attributo assente in meta' delle righe fa inciampare la ricerca in silenzio.
            if noti >= 500:
                r = [x for x in r if x.get("insider_storia") is not None]
            else:
                for x in r:
                    x.pop("insider_storia", None)
                    x.pop("insider_quanti_noti", None)
                print(f"   troppo poche pool col passato noto: l'attributo non entra "
                      f"nella ricerca", flush=True)

    # IL PASSATO DELL'ENTITA', NON DEL SINGOLO INDIRIZZO (3/10, idea di Nicolo').
    # «I portafogli con percentuali di successo collegati a main wallet»: una mano usa molti
    # indirizzi, e il passato di un indirizzo nuovo e' vuoto per costruzione. Il passato della
    # MANO non lo e'. Il legame che non si cambia a costo zero e' chi paga le prime commissioni.
    # Stessa regola di onesta' di insider_storia: si usano solo le monete il cui esito era NOTO
    # almeno sei ore prima della decisione. Senza quel vincolo compare un vantaggio che e'
    # informazione dal futuro — misurato il 1/10: +16% che svaniva a zero.
    percorso_fin = f"data/multichain/{chain}/finanziatori.json.gz"
    if os.path.exists(percorso_ins) and os.path.exists(percorso_fin):
        import collections
        try:
            fin = json.load(gzip.open(percorso_fin, "rt")).get("da", {})
        except Exception:
            fin = {}
        if fin:
            quante = collections.Counter(fin.values())
            storia_e = collections.defaultdict(list)
            chiusura = float(os.environ.get("ORE_CHIUSURA", 6)) * 3600
            noti = 0
            for x in r:
                chi = primi.get(x.get("_pool")) or []
                mani = {fin[w] for w in chi if w in fin}
                lim = x["_t"] - chiusura
                pre = [[e for t, e in storia_e[m] if t <= lim] for m in mani]
                pre = [h for h in pre if h]
                if pre:
                    x["entita_storia"] = float(np.mean([np.mean(h) for h in pre]))
                    x["entita_quante_mani"] = len(pre)
                    x["entita_portafogli"] = max(quante[m] for m in mani)
                    noti += 1
                else:
                    x["entita_storia"] = None
                    x["entita_quante_mani"] = 0
                    x["entita_portafogli"] = 0
                for m in mani:
                    storia_e[m].append((x["_t"], x["_bersaglio"]))
            print(f"   passato dell'ENTITA' noto per {noti:,} pool su {len(r):,} "
                  f"({100*noti/max(1,len(r)):.0f}%), {len(quante):,} mani conosciute", flush=True)
            # come per insider_storia: un attributo assente in meta' delle righe fa inciampare
            # la ricerca in silenzio. Entra solo se c'e' abbastanza materiale.
            if noti >= 500:
                r = [x for x in r if x.get("entita_storia") is not None]
            else:
                for x in r:
                    for k in ("entita_storia", "entita_quante_mani", "entita_portafogli"):
                        x.pop(k, None)
                print(f"   troppo poche pool con una mano nota: l'attributo non entra "
                      f"nella ricerca", flush=True)

    # IL PASSATO DI CHI HA LANCIATO LA MONETA (4/10).
    # La decomposizione del 4/10 (RILEVATORE_DI_AZZERAMENTI.md) dice che quattro quinti del
    # vantaggio che abbiamo vengono dall'EVITARE le monete che muoiono. E «quale moneta muore»
    # non e' una domanda di grafico: e' una domanda su CHI l'ha lanciata. Un lanciatore che ha
    # gia' fatto morire dieci monete e' il dato piu' vicino alla causa che possiamo avere.
    # Costa UNA lettura per gettone, non per scambio (agents/lanciatori.py).
    #
    # STESSA REGOLA DI ONESTA' di insider_storia, e non e' negoziabile: si usano solo le monete
    # il cui esito era NOTO almeno sei ore prima della decisione. Senza quel vincolo compare un
    # vantaggio che e' informazione dal futuro — misurato il 1/10: +16% che svaniva a zero.
    # E il numero di monete passate si porta ACCANTO, perche' e' il controllo di sopravvivenza:
    # un lanciatore ha un passato solo se e' ancora qui, e il 4/10 l'effetto ha retto proprio
    # perche' si e' guardato dentro lo stesso scaglione di quante-monete-note.
    percorso_lan = f"data/multichain/{chain}/lanciatori.json.gz"
    percorso_cop = f"data/multichain/{chain}/coppie.json"
    if os.path.exists(percorso_lan) and os.path.exists(percorso_cop):
        import collections
        try:
            # L'INVOLUCRO NON E' IL CONTENUTO (4/10). Qui leggevo l'archivio intero, che e'
            # {"acq": ..., "da": {...}}: iterando trovavo due chiavi invece di 2.710 gettoni,
            # nessuna con un lanciatore, e l'attributo si spegneva IN SILENZIO dicendo «troppe
            # poche pool». Lo stesso involucro mi aveva ingannato dieci minuti prima leggendo
            # la tabella dei profitti — due volte di seguito, perche' guardavo le chiavi
            # radice invece della forma del file.
            # IN POSITIVO: si prende "da" per nome, e se non c'e' niente dentro si URLA.
            # Un attributo che si spegne da solo e' peggio di uno che manca: sembra misurato.
            lan = json.load(gzip.open(percorso_lan, "rt")).get("da", {})
            cop = json.load(open(percorso_cop))["coppie"]
        except Exception:
            lan, cop = {}, {}
        if lan and cop:
            # quale lato e' il memecoin, ricavato dai dati: una valuta compare in migliaia di
            # coppie, un memecoin in una o due. Dedurlo dalla mappa sbagliata il 2/10 produsse
            # sedici milioni di dollari di perdite finte.
            quante_coppie = collections.Counter()
            for v2 in cop.values():
                for lato in ("t0", "t1"):
                    a = (v2.get(lato) or "").lower()
                    if len(a) == 42:
                        quante_coppie[a] += 1
            valute = {a for a, n in quante_coppie.items() if n > 50}
            gettone = {}
            for pid, v2 in cop.items():
                c = [a for a in ((v2.get(l) or "").lower() for l in ("t0", "t1"))
                     if len(a) == 42 and a not in valute]
                if len(c) == 1:
                    gettone[pid] = c[0]
            chi_lancia = {g.lower(): d["chi"].lower() for g, d in lan.items()
                          if isinstance(d, dict) and d.get("chi")}
            if lan and not chi_lancia:
                raise SystemExit(
                    f"COMBINAZIONI | {percorso_lan} ha {len(lan):,} voci e NESSUNA con un "
                    f"lanciatore: la forma del file non e' quella che mi aspetto. Mi fermo "
                    f"invece di spegnere l'attributo in silenzio.")
            storia_l = collections.defaultdict(list)
            chiusura = float(os.environ.get("ORE_CHIUSURA", 6)) * 3600
            noti = 0
            for x in r:
                g = gettone.get(x.get("_pool"))
                mano = chi_lancia.get(g) if g else None
                lim = x["_t"] - chiusura
                pre = [e for tt, e in storia_l[mano] if tt <= lim] if mano else []
                if pre:
                    x["lanciatore_storia"] = float(np.mean(pre))
                    x["lanciatore_quante_note"] = len(pre)
                    x["lanciatore_morte_passate"] = float(
                        np.mean([1.0 if e <= -0.99 else 0.0 for e in pre]))
                    noti += 1
                else:
                    # NON si mette zero: zero vuol dire «andavano in pari», non «non lo sappiamo»
                    x["lanciatore_storia"] = None
                    x["lanciatore_quante_note"] = 0
                    x["lanciatore_morte_passate"] = None
                if mano:
                    storia_l[mano].append((x["_t"], x["_bersaglio"]))
            print(f"   passato del LANCIATORE noto per {noti:,} pool su {len(r):,} "
                  f"({100*noti/max(1,len(r)):.0f}%), {len(chi_lancia):,} gettoni con un "
                  f"lanciatore, {len(storia_l):,} lanciatori distinti", flush=True)
            if noti >= 500:
                r = [x for x in r if x.get("lanciatore_storia") is not None]
            else:
                for x in r:
                    for k in ("lanciatore_storia", "lanciatore_quante_note",
                              "lanciatore_morte_passate"):
                        x.pop(k, None)
                print(f"   troppo poche pool con un lanciatore noto: l'attributo non entra "
                      f"nella ricerca", flush=True)

    import bisect
    tempi = [x["_t"] for x in r]
    for i, x in enumerate(r):
        a = bisect.bisect_left(tempi, x["_t"] - 3600)
        x["folla_ora_prima"] = i - a
        # l'ora del giorno: gratis, e i mercati non si comportano uguale alle 3 e alle 15
        x["ora_del_giorno"] = int((x["_t"] // 3600) % 24)
    return r


def condizioni(righe, nomi):
    """Ogni condizione e' «attributo sopra/sotto una soglia», con la soglia presa dai quantili.

    Le soglie si calcolano SOLO sul pezzo di ricerca: prenderle su tutto sarebbe gia' guardare
    il futuro, in una forma sottile che non si vede finche' non la si nomina.
    """
    fuori = []
    for k in nomi:
        v = np.array([float(x.get(k) or 0.0) for x in righe])
        if not np.isfinite(v).all() or v.std() == 0:
            continue
        for q in QUANTILI:
            s = float(np.quantile(v, q))
            fuori.append((f"{k}>{s:.4g}", k, ">", s))
            fuori.append((f"{k}<{s:.4g}", k, "<", s))
    return fuori


def maschera(righe, cond):
    _, k, verso, s = cond
    v = np.array([float(x.get(k) or 0.0) for x in righe])
    return v > s if verso == ">" else v < s


def cerca(righe_cerca, righe_scegli, esiti_cerca, esiti_scegli, nomi, rimescola=False, seme=0):
    """Torna (descrizione, media sul pezzo di scelta, quante righe) della combinazione migliore."""
    if rimescola:
        rng = np.random.default_rng(seme)
        esiti_cerca = rng.permutation(esiti_cerca)
        esiti_scegli = rng.permutation(esiti_scegli)
    conds = condizioni(righe_cerca, nomi)
    mc = {c[0]: maschera(righe_cerca, c) for c in conds}
    ms = {c[0]: maschera(righe_scegli, c) for c in conds}
    # si tengono solo le condizioni che da sole promettono qualcosa sul pezzo di RICERCA
    buone = []
    for c in conds:
        m = mc[c[0]]
        if m.sum() < MIN_POOL:
            continue
        buone.append((float(esiti_cerca[m].mean()), c[0]))
    buone.sort(reverse=True)
    buone = [n for _, n in buone[:40]]            # le 40 piu' promettenti, per non esplodere
    provate = 0
    classifica = []
    for quante in range(1, MAX_CONDIZIONI + 1):
        for combo in itertools.combinations(buone, quante):
            provate += 1
            m = np.ones(len(righe_cerca), bool)
            for n in combo:
                m &= mc[n]
            if m.sum() < MIN_POOL:
                continue
            # promossa dalla ricerca: ora si MISURA sul pezzo di scelta, mai visto finora
            m2 = np.ones(len(righe_scegli), bool)
            for n in combo:
                m2 &= ms[n]
            if m2.sum() < MIN_POOL // 2:
                continue
            r = float(esiti_scegli[m2].mean())
            classifica.append((r, " E ".join(combo), int(m2.sum())))
    # LE DIECI MIGLIORI, NON LA PRIMA (30/09 notte). Con 10.700 combinazioni, la migliore sul
    # pezzo di scelta e' anche la piu' fortunata: giudicarla da sola confonde il talento con la
    # fortuna. Se il segnale c'e', le dieci migliori battono il fondale IN MEDIA sul terzo pezzo.
    # Se non c'e', si disperdono intorno al fondale — ed e' una risposta piu' solida di una sola.
    classifica.sort(reverse=True)
    return classifica[:10], provate


def main():
    chain = os.environ.get("CHAIN", "robinhood")
    righe = carica(chain)
    nomi = sorted(k for k in righe[0] if not k.startswith("_"))
    # SI POSSONO METTERE DA PARTE ALCUNI ATOMI (2/10), per confrontare due famiglie di attributi
    # sugli STESSI pool e sugli stessi tagli di tempo. Serve a agents/porte_o_persone.py, dove
    # il criterio e' scritto prima di guardare i numeri.
    fuori = [x.strip() for x in os.environ.get("ESCLUDI_ATOMI", "").split(",") if x.strip()]
    if fuori:
        nomi = [k for k in nomi if k not in fuori]
        print(f"   messi da parte {len(fuori)} atomi: restano {len(nomi)}", flush=True)
    # LA MISURA DICHIARA CIO' CHE HA USATO (1/10). Il controllo «atomi-congelati» leggeva gli
    # attributi dal FILE dei dati: quando ne ho aggiunto uno qui nel codice, al caricamento, la
    # guardia non se n'e' accorta e ha detto «impronta invariata». La porta costruita stamattina
    # si scavalcava con la mossa che ho fatto io stesso un'ora dopo.
    # IN POSITIVO: qui si scrive l'elenco esatto che la ricerca ha usato, e la guardia controlla
    # QUESTO. Un controllo che guarda la fonte invece del consumo controlla la cosa sbagliata.
    import hashlib as _h
    os.makedirs("data", exist_ok=True)
    json.dump({"quando": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
               "chain": chain, "quanti": len(nomi),
               "impronta": _h.sha256(("|".join(nomi)).encode()).hexdigest()[:16],
               "atomi": nomi},
              open("data/atomi_usati.json", "w"), ensure_ascii=False, indent=1)
    esiti = np.array([x["_bersaglio"] for x in righe])
    n = len(righe)
    a, b = int(n * 0.45), int(n * 0.72)
    # TRE PEZZI DI TEMPO: cerco / scelgo / giudico. Il terzo non lo tocco fino alla fine.
    rc, rs, rg = righe[:a], righe[a:b], righe[b:]
    ec, es, eg = esiti[:a], esiti[a:b], esiti[b:]
    print(f"COMBINAZIONI | {chain}: {n:,} pool — cerco su {len(rc):,}, scelgo su {len(rs):,}, "
          f"giudico su {len(rg):,} mai visti", flush=True)

    dieci, provate = cerca(rc, rs, ec, es, nomi)
    if not dieci:
        print("   nessuna combinazione con abbastanza pool: non si giudica", flush=True)
        return
    r_vero, desc, quanti = dieci[0]
    print(f"   provate {provate:,} combinazioni di 1-{MAX_CONDIZIONI} condizioni incrociate",
          flush=True)
    print(f"   migliore sul pezzo di scelta: {100*r_vero:+.1f}% su {quanti} pool", flush=True)
    print(f"   -> {desc}", flush=True)

    # IL CONTROLLO SUL RUMORE: la stessa ricerca dove per costruzione non c'e' niente da trovare.
    # CINQUE RIMESCOLATE SONO TROPPO POCHE (1/10). Il metro e' il MASSIMO su N rimescolate:
    # con N=5 quel massimo balla, e su base e' uscito NEGATIVO (-3,2% e -15,3%). Un tetto
    # negativo fa passare qualunque cosa — e infatti tre configurazioni di base sono state
    # dichiarate «segnale» da un metro che non misurava niente.
    # Grok l'aveva detto: serve il 99mo percentile del massimo, non una stima su cinque prove.
    # IN POSITIVO: si rimescola RIMESCOLATE volte (20 per difetto) e il metro e' il massimo su
    # quelle. Costa qualche minuto in piu' per giro, e vale: una soglia che balla non e' una
    # soglia, e il costo di crederle e' rischiare soldi veri su niente.
    RIMESCOLATE = int(os.environ.get("RIMESCOLATE", 20))
    finti = []
    dieci_finti = []
    for s in range(RIMESCOLATE):
        d, _ = cerca(rc, rs, ec, es, nomi, rimescola=True, seme=s)
        if d:
            finti.append(d[0][0])
            dieci_finti.append(d)
    soglia = float(np.max(finti))
    print(f"   sul RUMORE la migliore fa {100*np.mean(finti):+.1f}% in media, "
          f"{100*soglia:+.1f}% nel caso migliore su {len(finti)} rimescolate", flush=True)

    if r_vero <= soglia:
        print(f"   VERDETTO: la migliore sul vero NON batte la migliore sul rumore. "
              f"Non abbiamo trovato niente.", flush=True)
        return

    # e solo se supera il rumore si apre il terzo pezzo, quello mai toccato
    conds = {c[0]: c for c in condizioni(rc, nomi)}
    print(f"\n   LE DIECI MIGLIORI, GIUDICATE SUL PEZZO MAI VISTO "
          f"(fondale {100*float(eg.mean()):+.1f}%):", flush=True)
    esiti_giudizio = []
    for r_s, d, _ in dieci:
        m = np.ones(len(rg), bool)
        for nome in d.split(" E "):
            if nome in conds:
                m &= maschera(rg, conds[nome])
        if m.sum() < MIN_POOL // 3:
            print(f"      {100*r_s:+7.1f}% -> solo {int(m.sum())} pool, non giudicabile",
                  flush=True)
            continue
        g = float(eg[m].mean())
        esiti_giudizio.append(g)
        print(f"      {100*r_s:+7.1f}% sulla scelta -> {100*g:+7.1f}% sul giudizio "
              f"({int(m.sum())} pool)   {d[:70]}", flush=True)
    def margine_di(dieci_combinazioni):
        """Il margine sul pezzo di giudizio per un insieme di dieci combinazioni."""
        v = []
        for _r, dd, _q in dieci_combinazioni:
            mm = np.ones(len(rg), bool)
            for n_ in dd.split(" E "):
                if n_ in conds:
                    mm &= maschera(rg, conds[n_])
            if mm.sum() >= MIN_POOL // 3:
                v.append(float(eg[mm].mean()))
        return (float(np.mean(v)) - float(eg.mean())) if v else None

    if esiti_giudizio:
        med = float(np.mean(esiti_giudizio))
        fon = float(eg.mean())
        # LA SOGLIA SI MISURA, NON SI POSTULA (1/10, da una revisione di Grok: «la tua soglia
        # 0,10 + 0,02*log2(n) e' cosmetica»). Qui sopra il rumore gia' faceva da metro, ma solo
        # sul pezzo di SCELTA; il margine sul pezzo di giudizio veniva confrontato con una
        # formula. Misurato: la formula chiedeva il 46% mentre il caso fortunato sulla scelta
        # arrivava al 16,7% — tre volte il tetto del rumore, cioe' una porta che non si apre
        # mai, nemmeno per un vantaggio vero.
        # IN POSITIVO: si giudicano sul pezzo mai visto anche le dieci combinazioni scelte
        # dalle ricerche SUL RUMORE — combinazioni che per costruzione non possono sapere
        # niente — e il loro margine migliore e' il metro. Costa quasi niente: la ricerca sul
        # rumore era gia' fatta, qui si aggiunge solo il giudizio.
        margini_finti = [x for x in (margine_di(d) for d in dieci_finti) if x is not None]
        tetto = float(np.max(margini_finti)) if margini_finti else None
        if tetto is not None:
            print(f"   IL METRO MISURATO: le combinazioni scelte dal caso, giudicate sul pezzo "
                  f"mai visto, fanno un margine fino a {100*tetto:+.1f}% "
                  f"(su {len(margini_finti)} rimescolate; mediana {100*float(np.median(margini_finti)):+.1f}%)",
                  flush=True)
        vero = med - fon
        # IL MARGINE SUL FONDALE NON E' UN GUADAGNO (1/10). Il margine confronta la media di un
        # sottoinsieme PICCOLO con la media di TUTTO. Ma la media di tutto e' trascinata da
        # pochi vincitori enormi, quindi qualunque sottoinsieme piccolo «perde» contro di essa:
        # il metro misurato sulle rimescolate e' uscito NEGATIVO (-8,8% su venti rimescolate),
        # cioe' tutte e venti le selezioni casuali facevano peggio del fondale. Sistematico,
        # non casuale.
        # Conseguenza: «battere il fondale» e' facile e non vuol dire guadagnare. Il miglior
        # «segnale» di oggi aveva margine +30,4% e rendimento assoluto -2,8%: si perde comunque.
        # Grok l'aveva chiesto: «il limite inferiore del risultato, al prezzo che paghi, alla
        # taglia che esegui, sopra zero».
        # IN POSITIVO: due porte, e servono entrambe. (1) il margine batte il metro misurato,
        # (2) il rendimento ASSOLUTO delle dieci migliori e' sopra zero. Perdere meno del
        # mercato non e' un vantaggio: e' una perdita piu' piccola, e non si incassa.
        batte_il_caso = (vero > 0.05) if tetto is None else (vero > tetto)
        guadagna = med > 0
        esito = "SEGNALE" if (batte_il_caso and guadagna) else "NIENTE"
        if batte_il_caso and not guadagna:
            print(f"   batte il caso MA il rendimento assoluto e' {100*med:+.1f}%: si perde "
                  f"comunque, solo meno del mercato. NON e' un vantaggio.", flush=True)
        print(f"\n   IN MEDIA le dieci migliori fanno {100*med:+.1f}% contro un fondale di "
              f"{100*fon:+.1f}%: {esito}", flush=True)
        if tetto is not None:
            print(f"   margine vero {100*vero:+.1f}% contro il metro {100*tetto:+.1f}%",
                  flush=True)


if __name__ == "__main__":
    main()
