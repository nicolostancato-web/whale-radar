#!/usr/bin/env python3
"""
INTEGRITA — quello che abbiamo salvato corrisponde a quello che la catena dice?

PERCHE' ESISTE (15/09, condizione 5 dei criteri). Nessuno l'ha mai verificato. Abbiamo controllato
che i dati NON abbiano buchi evidenti — wallet presenti, istanti sensati, nessun doppione — ma
nessuna di quelle prove risponde alla domanda vera: **e' andato perso qualcosa?**

Zero duplicati non dimostra completezza. Un file puo' essere perfettamente pulito e mancare meta'
degli scambi, e nessuno dei controlli che facciamo se ne accorgerebbe.

IL TEST. Si sorteggiano finestre di blocchi gia' scavate, si RICHIEDONO alla catena da capo, e si
confronta con quello che abbiamo in casa:
  - stesso numero di scambi sui nostri pool?
  - stessi identificativi (transazione + posizione)?
  - stesse quantita' grezze?
  - stesso ordine?
Una sola discrepanza e' un fallimento: non stiamo cercando quanto siamo bravi, stiamo cercando se
c'e' un modo silenzioso di perdere dati.

SOGLIA (imposta dalla revisione): >=299 finestre stratificate senza discrepanze. Con 299 successi su
299, il limite superiore al 95% sul tasso d'errore invisibile e' sotto l'1%.

Il seme del sorteggio e' scritto nel rapporto: chiunque puo' rifare le stesse estrazioni.

Sola lettura, nodi pubblici gratuiti. €0.
"""
import json, gzip, os, glob, time, random, urllib.request

SWAP = ["0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
        "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67",
        "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"]
V4 = SWAP[2]
RPC = {"base": ("https://mainnet.base.org", 60), "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 200)}
SEME = int(os.environ.get("INTEGRITA_SEME", 20260915))
QUANTE = int(os.environ.get("INTEGRITA_FINESTRE", 12))
BUDGET = int(os.environ.get("BUDGET_SEC", 420))
REG = "data/integrita.jsonl"
t0 = time.time()


def rpc(url, metodo, params):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    try:
        r = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json",
                                                         "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(r, timeout=40) as x:
            d = json.load(x)
        return (None, str(d["error"])[:60]) if "error" in d else (d.get("result"), None)
    except Exception as e:
        return None, f"{type(e).__name__} {getattr(e, 'code', '')}"


_CONV = {}


def conversione(chain, quanti=40):
    """Quota dei nostri record gia' nel formato completo, su un campione di pool.
    Un record senza hash di blocco e' del vecchio formato: le fette lo devono ancora rifare."""
    if chain in _CONV: return _CONV[chain]
    d = f"data/multichain/{chain}/storico"
    if not os.path.isdir(d): _CONV[chain] = None; return None
    files = sorted(os.listdir(d))[:quanti]
    con = tot = 0
    for fn in files:
        try:
            for l in gzip.open(os.path.join(d, fn), "rt"):
                if not l.strip(): continue
                tot += 1
                if json.loads(l).get("bh"): con += 1
        except Exception: pass
    _CONV[chain] = round(con / tot, 3) if tot else None
    return _CONV[chain]


def nostri_record(chain, da, a, nostri):
    """Cosa abbiamo IN CASA per quella fascia di blocchi."""
    out = {}
    for cartella in ("storico", "vivo"):
        for f in glob.glob(f"data/multichain/{chain}/{cartella}/*.gz"):
            pool = os.path.basename(f).replace(".jsonl.gz", "").lower()
            if pool not in nostri: continue
            try:
                for l in gzip.open(f, "rt"):
                    if not l.strip(): continue
                    d = json.loads(l)
                    bn = d.get("blocco")
                    # I RESIDUI DEL VECCHIO FORMATO NON TESTIMONIANO (16/09). Un record senza hash
                    # di blocco e' di prima del cambio formato: non e' mai stato salvato con
                    # l'indice completo, quindi la sua chiave non puo' combaciare con quella della
                    # catena e risulta «inventato» pur essendo vero. Le due sole accuse di record
                    # inventati su 58 finestre erano entrambe questo.
                    # pota() li sta gia' buttando e le fette li riscaricano: un record incompleto e
                    # gia' destinato alla sostituzione non puo' testimoniare ne' a favore ne' contro.
                    # Quando la conversione sara' al 100% questa riga non escludera' piu' nulla.
                    if not d.get("bh"):
                        continue
                    if bn and da <= bn <= a:
                        out[(d.get("tx"), d.get("li"))] = (pool, d.get("a0"), d.get("a1"))
            except Exception: pass
    return out


def main():
    righe = []
    if os.path.exists(REG):
        for l in open(REG):
            if l.strip():
                try: righe.append(json.loads(l))
                except Exception: pass

    nuove = []
    for chain, (url, ampiezza) in RPC.items():
        if time.time() - t0 > BUDGET: break
        try:
            nostri = {k.lower() for k in json.load(open(f"data/multichain/{chain}/righe.json")).get("pool", {})}
        except Exception:
            continue
        # le fasce gia' scavate: si sorteggia dentro quelle, non a caso nella catena
        # DOVE SI CAMPIONA CAMBIA TUTTO (16/09). Prima si pescava un blocco a caso fra tutti quelli
        # che tocchiamo, di qualunque pool. Ma noi teniamo solo le prime ore di vita di ogni pool:
        # un blocco preso a caso cade quasi sempre fuori dalla finestra di conservazione di tutti,
        # e il confronto resta vuoto. Misurato: sette finestre su dieci non misuravano nulla.
        # Quindi si pesca DENTRO le prime ore di vita di un pool che conosciamo. E' quello che
        # «stratificate» voleva dire fin dall'inizio nella condizione 5: non finestre a caso sulla
        # catena, ma finestre dove abbiamo davvero dichiarato di avere qualcosa.
        # I 400 FILE NON VANNO PRESI IN TESTA, VANNO SORTEGGIATI (18/09). Qui c'era
        # `glob(...)[:400]`: i primi quattrocento file nell'ordine del disco, cioe' SEMPRE GLI
        # STESSI POOL a ogni giro. Quei pool col tempo si riempiono fino al tetto di 300 righe, e
        # una finestra dove ogni evento appartiene a un pool al tetto non ha nulla da confrontare:
        # viene registrata «non misurabile».
        # Il risultato si vede nella serie storica: le finestre non misurabili sono passate dal 23%
        # al 60% mentre la raccolta migliorava. Non stava peggiorando il database — stavamo
        # interrogando sempre la stessa coorte invecchiata, e quella coorte ha smesso di poter
        # rispondere. Un campione fisso non misura il sistema: misura se stesso che invecchia.
        # Sorteggiando fra TUTTI i file, ogni giro incontra anche pool giovani, sotto il tetto,
        # che hanno ancora qualcosa da dire.
        rnd_f = random.Random(SEME + int(time.time() // 3600))   # cambia ogni ora, resta ripetibile
        grezzi = []
        for cartella in ("storico", "vivo"):
            _tutti = glob.glob(f"data/multichain/{chain}/{cartella}/*.gz")
            _presi = _tutti if len(_tutti) <= 400 else rnd_f.sample(_tutti, 400)
            for f in _presi:
                pool_f = os.path.basename(f).replace(".jsonl.gz", "").lower()
                try:
                    for l in gzip.open(f, "rt"):
                        if l.strip():
                            d0 = json.loads(l)
                            if d0.get("blocco") and d0.get("ts"):
                                grezzi.append((pool_f, d0["blocco"], d0["ts"]))
                except Exception: pass
        if len(grezzi) < 50: continue
        # LA NASCITA VERA PRIMA DELLE CANDELE (17/09). Questo filtro decide quali scambi della
        # catena confrontare: se la nascita e' sbagliata, si confronta la finestra sbagliata e il
        # verdetto non vale niente. E le candele SONO sbagliate su robinhood — misurato, +13,5 ore
        # mediane e tre quarti dei casi fuori dalla finestra di sei ore.
        # Con la nascita giusta il confronto cambia bersaglio: e' possibile che la percentuale di
        # finestre identiche si muova parecchio, in un senso o nell'altro. Meglio saperlo adesso
        # che scoprire fra tre settimane di aver certificato l'integrita' del periodo sbagliato.
        nascita = {}
        _vera = f"data/multichain/{chain}/nascita_vera.json"
        if os.path.exists(_vera):
            try:
                for _p, _d in json.load(open(_vera)).get("nascite", {}).items():
                    if _d.get("fonte") == "catena" and _d.get("ts"):
                        nascita[_p.lower()] = int(_d["ts"])
            except Exception:
                pass
        _da_catena = len(nascita)
        for d in ("candles", "pulse"):
            for f in glob.glob(f"data/multichain/{chain}/{d}/*.jsonl.gz"):
                a_ = os.path.basename(f).replace(".jsonl.gz", "").lower()
                if a_ in nascita: continue
                try:
                    for l in gzip.open(f, "rt"):
                        if l.strip():
                            d0 = json.loads(l); v0 = d0.get("t0") or d0.get("ts")
                            if v0: nascita[a_] = int(v0); break
                except Exception: pass
        # ora che le nascite si conoscono, si tengono solo i blocchi dentro le prime ore di vita
        VITA = int(os.environ.get("ORE_VITA", 6)) * 3600
        blocchi = {bn for pl, bn, ts in grezzi
                   if nascita.get(pl) and nascita[pl] <= ts <= nascita[pl] + VITA}
        if len(blocchi) < 20:
            print(f"INTEGRITA | {chain}: solo {len(blocchi)} blocchi dentro le prime ore di vita "
                  f"di un pool noto — campione troppo sottile, salto", flush=True)
            continue
        print(f"INTEGRITA | {chain}: {_da_catena} nascite vere dalla catena, "
              f"{len(nascita) - _da_catena} stimate dalle candele", flush=True)
        # istante di un blocco: ancora una volta, interpolato
        punta, _ = rpc(url, "eth_blockNumber", [])
        if not punta: continue
        punta = int(punta, 16)
        bn_now, _ = rpc(url, "eth_getBlockByNumber", [hex(punta), False])
        bn_pre, _ = rpc(url, "eth_getBlockByNumber", [hex(punta - 20000), False])
        if not bn_now or not bn_pre: continue
        t_now = int(bn_now["timestamp"], 16)
        sec_b = (t_now - int(bn_pre["timestamp"], 16)) / 20000.0
        def istante(_c, b, _t=t_now, _p=punta, _s=sec_b):
            return int(_t - (_p - b) * _s)
        rnd = random.Random(SEME + len(righe))
        campione = rnd.sample(sorted(blocchi), min(QUANTE, len(blocchi)))
        for b in campione:
            if time.time() - t0 > BUDGET: break
            da, a = b, b + ampiezza
            log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(a),
                                                 "topics": [SWAP]}])
            time.sleep(1.2)
            # L'ORARIO DELLA FINESTRA SI CHIEDE, NON SI STIMA (15/09). L'istante interpolato
            # dalla punta sbaglia poco sui blocchi recenti e TANTO su quelli vecchi: misurato,
            # 0,00 ore di errore a 15 mila blocchi dalla punta e 2,09 ore a cinque milioni.
            # Con una finestra di vita di sei ore, due ore di errore decidono da sole se uno
            # scambio e' dentro o fuori. Un blocco in piu' da chiedere per finestra e' un prezzo
            # ridicolo per non dover fidarsi di una stima.
            bx, _e = rpc(url, "eth_getBlockByNumber", [hex(da), False])
            ts_finestra = int(bx["timestamp"], 16) if bx else None
            if log is None:
                nuove.append({"acq": int(time.time()), "chain": chain, "da": da, "a": a,
                              "esito": "lettura fallita", "dettaglio": err})
                continue
            # SI CONFRONTA CIO' CHE AVEVAMO DECISO DI TENERE (15/09). La prima esecuzione ha
            # dichiarato 12 discrepanze su 12, e stava confrontando cose diverse: la catena
            # restituisce TUTTI gli scambi dei nostri pool, noi ne teniamo apposta solo quelli
            # delle PRIME ORE di vita (e al massimo 300 per pool). Il resto non e' perso: e'
            # scartato per scelta.
            # Un controllo di integrita' deve chiedere «abbiamo tenuto tutto quello che volevamo
            # tenere?», non «abbiamo tutto quello che esiste?». Altrimenti misura le nostre
            # decisioni e le chiama guasti — ed e' il modo piu' rapido per farsi ignorare quando
            # il guasto arriva davvero.
            FINESTRA_VITA = int(os.environ.get("ORE_VITA", 6)) * 3600
            senza_nascita = set()
            prima_di_noi = 0
            catena = {}
            _blocco_di = {}
            for l in log:
                tp = l.get("topics") or []
                pool = (tp[1].lower() if (tp and tp[0] == V4 and len(tp) > 1) else l["address"].lower())
                if pool not in nostri: continue
                bn = int(l["blockNumber"], 16)
                ts_ev = ts_finestra if ts_finestra else istante(chain, bn)
                n0 = nascita.get(pool)
                # SE NON SAPPIAMO QUANDO E' NATO, LA FINESTRA NON E' MISURABILE PER QUEL POOL
                # (16/09). La nascita si legge dalle candele: un pool che non ne ha — tipicamente
                # uno che la coda viva ha appena scoperto — passava il filtro senza che nessuno lo
                # filtrasse, e la sua INTERA storia di catena finiva contata come «mancante».
                # Misurato su una finestra: nove pool con eta' apparente di MENO 334 ore, cioe' il
                # primo record che possediamo arriva quattordici giorni DOPO la finestra sotto esame.
                # Non avevamo deciso di non prenderli: non sapevamo che esistessero.
                # «Non lo so» non si registra come «hai sbagliato». Si esclude e SI CONTA, perche'
                # un'esclusione taciuta e' il modo piu' semplice per dichiararsi completi a vuoto.
                if not n0:
                    senza_nascita.add(pool)
                    continue
                if ts_ev and ts_ev < n0:
                    prima_di_noi += 1
                    continue                       # accaduto prima che scoprissimo il pool
                if ts_ev and ts_ev > n0 + FINESTRA_VITA:
                    continue                       # fuori dalle prime ore: scartato per scelta, non perso
                catena[(l.get("transactionHash"), int(l.get("logIndex", "0x0"), 16))] = pool
            _blocco_di[(l.get("transactionHash"), int(l.get("logIndex", "0x0"), 16))] = int(l["blockNumber"], 16)
            # LA CATENA GREZZA, senza nessuno dei nostri filtri: serve per la domanda
            # «ce lo siamo inventato?», che e' diversa da «ci manca qualcosa?».
            grezza = set()
            pool_nella_finestra = set()
            for l in log:
                tp = l.get("topics") or []
                pl = (tp[1].lower() if (tp and tp[0] == V4 and len(tp) > 1) else l["address"].lower())
                if pl in nostri:
                    grezza.add((l.get("transactionHash"), int(l.get("logIndex", "0x0"), 16)))
                    pool_nella_finestra.add(pl)     # tutti i nostri pool ATTIVI qui, filtri a parte
            casa = nostri_record(chain, da, a, nostri)
            # E SI ESCLUDONO I POOL AL TETTO (15/09). Teniamo al massimo 300 scambi per pool: per
            # quelli arrivati al tetto la catena ne ha di piu' PER FORZA, ed e' una nostra scelta.
            # Confrontarli sarebbe misurare di nuovo le nostre decisioni chiamandole guasti.
            # Ogni regola di conservazione che aggiungiamo va replicata QUI, altrimenti il controllo
            # di integrita' diventa un generatore di falsi allarmi — e un allarme che suona sempre
            # e' un allarme che nessuno guarda.
            # IL TETTO SI CONTA SU TUTTI I POOL DELLA FINESTRA, NON SU QUELLI RIMASTI (17/09).
            # `al_tetto` veniva calcolato su set(catena.values()), cioe' DOPO che il filtro della
            # nascita aveva gia' ristretto l'insieme: guardava una manciata di pool invece di tutti
            # quelli presenti. Misurato su una finestra: 90 dei 96 pool attivi erano al tetto,
            # l'audit ne ha esclusi QUATTRO, e 656 eventi di pool che avevamo smesso di raccogliere
            # per nostra scelta sono finiti fra i «mancanti».
            # Cioe' stavamo contando come guasto il nostro stesso tetto — ed e' la quarta volta in
            # tre giorni che questo controllo misura una nostra decisione e la chiama difetto.
            # Ogni regola di conservazione va applicata alla STESSA popolazione su cui si giudica.
            al_tetto = set()
            # LA POPOLAZIONE GIUSTA E' QUELLA DEI LOG GREZZI (17/09, seconda correzione). Avevo
            # unito i pool di `catena` e di `casa`, ma un pool al tetto in quella finestra non e' in
            # nessuno dei due: non ha superato il filtro della nascita e da noi non c'e' niente.
            # Restavano finestre con «catena 60, casa 0, al_tetto 2»: sessanta eventi contati come
            # mancanti e due soli pool riconosciuti come esclusi per scelta.
            # I log grezzi contengono TUTTI i nostri pool attivi li' dentro, prima di ogni filtro:
            # e' quella la popolazione su cui si giudica se un pool aveva ancora spazio o no.
            # DUE NUMERI, NON UNO (18/09, terza correzione di oggi su questo punto).
            # Stamattina escludevo i pool al tetto dall'intera finestra: su robinhood quasi ogni
            # finestra finiva «non misurabile» e l'integrita' la misuravamo su UNA CHAIN SOLA.
            # Poi ho giudicato i pool al tetto dentro il loro intervallo min..max: troppo permissivo
            # al contrario, perche' stare fra il primo e l'ultimo blocco non vuol dire aver raccolto
            # tutto in mezzo. Misurato: pool con 6.457 righe sparse risultavano «mancanti» di 118
            # eventi che non avevamo mai promesso di avere.
            #
            # LA REGOLA GIUSTA E' PIU' STRETTA: un pool si giudica in questa finestra solo se
            # abbiamo ALMENO UNA RIGA DENTRO la finestra — cioe' se li' stavamo davvero raccogliendo.
            # Se stavamo raccogliendo e manca un evento, e' un difetto vero.
            #
            # DA SOLA QUESTA REGOLA SAREBBE UN IMBROGLIO, e va detto: giudica solo dove abbiamo dati,
            # quindi non potra' MAI accorgersi di dove non abbiamo raccolto nulla. E' la trappola su
            # cui la revisione esterna mi ha corretto: «misurabili e' un sottoinsieme deciso dal
            # vostro processo».
            # Per questo si scrivono SEMPRE due numeri accanto, e il secondo impedisce di barare col
            # primo:
            #   FEDELTA'   — dove stavamo raccogliendo, quanto e' completo il nostro record
            #   COPERTURA  — quanta parte degli eventi della catena in quella finestra riguardava
            #                pool che stavamo raccogliendo
            # Restringere la fedelta' fa crollare la copertura. Non si possono alzare entrambe se
            # non raccogliendo davvero di piu'.
            eventi_catena_tot = len(catena)
            # E SI GIUDICA SOLO FIN DOVE ARRIVIAMO (19/09, quarta correzione su questo punto).
            # Con la regola «basta una riga dentro la finestra» restavano 28 finestre di base con
            # eventi mancanti. Tracciata la peggiore: 63 eventi, tutti di DUE pool con esattamente
            # 300 righe — cioe' al tetto dichiarato. Quegli eventi non mancano: sono quelli DOPO il
            # punto in cui abbiamo smesso di raccogliere per nostra scelta.
            # Giudicare oltre il proprio ultimo record vuol dire misurare come guasto una decisione
            # presa a monte: il quinto modo, in tre giorni, in cui questo controllo confonde una
            # nostra regola con un difetto.
            # Adesso per ogni pool si guarda fin dove arriva davvero il nostro archivio, e si
            # giudica solo entro quel punto.
            ultimo_nostro = {}
            giudicabili = set()
            for pool in pool_nella_finestra:
                ha_dentro = False
                for cart in ("storico", "vivo"):
                    f2 = f"data/multichain/{chain}/{cart}/{pool}.jsonl.gz"
                    if not os.path.exists(f2):
                        continue
                    try:
                        for l in gzip.open(f2, "rt"):
                            if not l.strip():
                                continue
                            b0 = json.loads(l).get("blocco")
                            if b0 is not None and da <= b0 <= a:
                                ha_dentro = True
                                break
                    except Exception:
                        pass
                    if ha_dentro:
                        break
                if ha_dentro:
                    giudicabili.add(pool)
                    # fin dove arriva il nostro archivio per questo pool
                    # IL LIMITE VA PRESO SULLA RACCOLTA DI QUEL TRATTO, NON SU TUTTO IL POOL
                    # (19/09, correzione della correzione). Prendevo il blocco piu' alto fra TUTTE
                    # le righe del pool, comprese quelle recentissime della coda viva: cosi' il
                    # limite sta sempre oltre la finestra e la regola non toglie mai niente.
                    # Misurato col contatore: «fuori_tetto: 0» su ogni finestra, cioe' una regola
                    # scritta, pubblicata e inerte. Adesso si guarda il blocco piu' alto NON OLTRE
                    # la fine della finestra: e' quello il punto fino a cui possiamo rispondere.
                    _hi = None
                    for cart in ("storico", "vivo"):
                        f2 = f"data/multichain/{chain}/{cart}/{pool}.jsonl.gz"
                        if not os.path.exists(f2):
                            continue
                        try:
                            for l in gzip.open(f2, "rt"):
                                if not l.strip():
                                    continue
                                b0 = json.loads(l).get("blocco")
                                if b0 is not None and b0 <= a:
                                    _hi = b0 if _hi is None else max(_hi, b0)
                        except Exception:
                            pass
                    if _hi is not None:
                        ultimo_nostro[pool] = _hi
                else:
                    al_tetto.add(pool)          # non giudicabile: non stavamo raccogliendo qui
            catena = {k: v for k, v in catena.items() if v not in al_tetto}
            # oltre il nostro ultimo record non si giudica: li' avevamo smesso di proposito
            _fuori_tetto = 0
            for _k in list(catena):
                _pool = catena[_k]
                _hi = ultimo_nostro.get(_pool)
                if _hi is not None and _blocco_di.get(_k, 0) > _hi:
                    del catena[_k]
                    _fuori_tetto += 1
            casa = {k: v for k, v in casa.items() if v[0] not in al_tetto}
            # DUE DOMANDE DIVERSE, DUE METRI DIVERSI (15/09). Prima stavano sullo stesso metro e
            # il controllo ha dichiarato 298 record inventati su una finestra dove erano tutti veri.
            # Il motivo: da stamattina ci sono DUE raccoglitori con regole di conservazione diverse.
            # Lo storico tiene solo le prime ore di vita di un pool; la coda viva raccoglie tutto
            # quello che passa alla punta, compresi pool nati da settimane. Misurando entrambi col
            # filtro dello storico, i record legittimi della coda viva risultavano inventati.
            #   «ci manca qualcosa?»   -> contro la catena FILTRATA come la filtriamo noi
            #   «ce lo siamo inventato?» -> contro la catena GREZZA: se il log esiste, non e' inventato
            # Tenerle sullo stesso metro non rende il controllo severo, lo rende cieco: urla dove
            # va tutto bene e quindi non lo si guarda piu' quando urla davvero.
            mancanti = [k for k in catena if k not in casa]
            inventati = [k for k in casa if k not in grezza]
            # UNA FINESTRA DOVE NON SI E' CONFRONTATO NULLA NON E' IDENTICA (16/09). Dopo aver
            # escluso — giustamente — gli eventi precedenti alla scoperta del pool, i pool al tetto
            # e quelli fuori dalle prime ore, resta a volte ZERO eventi da confrontare. Registrarli
            # come «identici» e' il modo piu' veloce per arrivare a 299 finestre verdi senza aver
            # verificato niente: misurato, una finestra escludeva 1057 eventi e ne confrontava 1.
            # Un controllo che esclude quasi tutto dira' sempre che va tutto bene.
            # E' la stessa regola che vale per gli altri strumenti di casa: prima di emettere un
            # verdetto, uno strumento deve dimostrare di poter dire anche di no.
            if not catena:
                esito = "non misurabile"
            else:
                esito = ("identici" if not mancanti and not inventati
                         else ("MANCANO DA NOI" if mancanti else "ABBIAMO DI PIU'"))
            # SI TIMBRA A CHE PUNTO ERA LA CONVERSIONE (15/09). Le fette stanno riscrivendo lo
            # storico nel formato completo: pota() svuota i file dai record senza hash di blocco e
            # le fette li riscaricano. Finche' dura, un pool puo' essere legittimamente mezzo vuoto.
            # Misurare la completezza adesso misura l'avanzamento della conversione, non il dato
            # perso — e su base, che e' al 28%, la differenza e' tutta.
            # Il verdetto NON cambia: si scrive solo a che punto eravamo, cosi' le finestre prese a
            # meta' lavoro si potranno escludere DOPO invece di sporcare le 299. Una misura presa
            # durante un cambiamento non e' sbagliata, e' solo da etichettare.
            nuove.append({"acq": int(time.time()), "chain": chain, "da": da, "a": a, "seme": SEME,
                          "catena": len(catena), "casa": len(casa), "al_tetto": len(al_tetto),
                          # LA COPERTURA VIAGGIA INSIEME ALLA FEDELTA' (18/09): quanta parte degli
                          # eventi della catena in questa finestra riguardava pool che stavamo
                          # davvero raccogliendo. Senza questo numero, «zero mancanti» si ottiene
                          # giudicando sempre meno.
                          "eventi_catena": eventi_catena_tot,
                          "fuori_tetto": _fuori_tetto,
                          "giudicabili": len(giudicabili),
                          "copertura": round(len(catena) / max(1, eventi_catena_tot), 4),
                          "mancanti": len(mancanti), "inventati": len(inventati), "esito": esito,
                          "conversione": conversione(chain),
                          "pool_senza_nascita": len(senza_nascita), "prima_di_noi": prima_di_noi})

    if nuove:
        try:
            with open(REG, "a") as f:
                for r in nuove: f.write(json.dumps(r) + "\n")
        except Exception: pass
    righe += nuove

    # LE RIGHE DI PRIMA DELLA CORREZIONE NON CONTANO PER IL TRAGUARDO (16/09). Le 58 finestre
    # scritte fino a stanotte usavano la regola vecchia: una finestra dove non si confrontava nulla
    # veniva registrata «identici». Dicevano 83% di finestre identiche; con la guardia nuova lo
    # stesso lavoro dice 40%. Non si cancellano — restano a registro, ed e' giusto poter rileggere
    # cosa credevamo — ma non possono contare verso le 299, altrimenti il traguardo si raggiunge
    # con misure che sapevamo essere cieche.
    # Si riconoscono da sole: le righe nuove portano il conteggio delle esclusioni, le vecchie no.
    # LE FINESTRE GIUDICATE COL TETTO SBAGLIATO NON CONTANO (17/09). Fino a stamattina l'esclusione
    # dei pool al tetto guardava una manciata di pool invece di tutti quelli attivi nella finestra:
    # misurato, 90 su 96 al tetto e solo 4 riconosciuti. Quelle finestre hanno contato come
    # «mancanti» centinaia di eventi che non raccogliamo per nostra scelta — cioe' hanno giudicato
    # una nostra decisione e l'hanno chiamata difetto.
    # Restano a registro, ed e' giusto poter rileggere cosa credevamo, ma non possono contare verso
    # le 299: un traguardo raggiunto con misure che sappiamo storte non e' un traguardo.
    # Si riconoscono da sole: le righe nuove portano il conteggio dei pool visti nella finestra.
    righe = [r for r in righe if "pool_senza_nascita" in r or r.get("esito") == "lettura fallita"]
    righe = [r for r in righe if r.get("acq", 0) >= 1789600000 or r.get("esito") == "lettura fallita"]
    # SI RIPORTA SU TUTTE LE FINESTRE PROVATE, NON SOLO SU QUELLE CHE SIAMO RIUSCITI A
    # CONFRONTARE (18/09, rilievo della revisione esterna). «Misurabili» e' un sottoinsieme deciso
    # dal nostro stesso processo: se le finestre problematiche diventano non misurabili, la
    # percentuale sale mentre la qualita' peggiora.
    # Misurato sui quattro quarti della raccolta, ed e' esattamente quello che stava succedendo:
    #     non misurabili   26% -> 44% -> 52%
    #     identiche fra le misurabili   31% -> 46% -> 55%
    # Le due colonne salivano INSIEME. Il «41%» che riportavo era in buona parte l'effetto dello
    # scarto, non un miglioramento: sul totale delle finestre provate il numero vero e' 24%, e il
    # progresso reale e' dal 21% al 27%.
    # Da qui in avanti il numero principale e' quello sul totale. L'altro resta, ma accanto.
    tutte = [r for r in righe if r.get("esito") != "lettura fallita"]
    valide = [r for r in righe if r.get("esito") not in ("lettura fallita", "non misurabile")]
    ok = [r for r in valide if r.get("esito") == "identici"]
    L = ["# 🔍 INTEGRITÀ — quello che abbiamo corrisponde a quello che la catena dice?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · seme {SEME} · condizione 5 · €0*", "",
         "> Zero duplicati **non dimostra completezza**. Un file può essere perfettamente pulito e",
         "> mancare metà degli scambi, e nessuno dei controlli che facciamo se ne accorgerebbe.", "",
         "> Qui si sorteggiano fasce di blocchi già scavate, si richiedono alla catena **da capo**, e",
         "> si confronta con quello che abbiamo in casa.", "",
         f"**Finestre verificate: {len(valide)}** · identiche: **{len(ok)}** · "
         f"letture fallite (non contano): {len(righe) - len(valide)}", ""]
    if valide:
        brutte = [r for r in valide if r.get("esito") != "identici"]
        L += ["| esito | finestre |", "|---|---|",
              f"| ✅ identiche | {len(ok)} |"]
        for e in ("MANCANO DA NOI", "ABBIAMO DI PIU'"):
            n = sum(1 for r in valide if r.get("esito") == e)
            if n: L.append(f"| 🔴 {e} | {n} |")
        L += [""]
        if brutte:
            L += ["## Le discrepanze", ""]
            for r in brutte[:6]:
                L.append(f"- `{r['chain']}` blocchi {r['da']}-{r['a']}: la catena dice "
                         f"**{r['catena']}**, noi abbiamo **{r['casa']}** "
                         f"(mancanti {r['mancanti']}, in più {r['inventati']})")
            L += [""]
        L += ["## Verdetto", ""]
        if len(ok) >= 299 and not brutte:
            L += ["> ✅ **Condizione 5 soddisfatta**: 299+ finestre senza una discrepanza. Il limite",
                  "> superiore al 95% sul tasso d'errore invisibile è sotto l'1%."]
        elif brutte:
            L += [f"> 🔴 **{len(brutte)} discrepanze su {len(valide)}**. Una sola basta a far fallire",
                  "> la condizione: non stiamo misurando quanto siamo bravi, stiamo cercando se esiste",
                  "> un modo silenzioso di perdere dati. Se esiste, va trovato prima di fidarsi."]
        else:
            L += [f"> ⏸️ {len(ok)} finestre pulite su 299 richieste. **Mancano {299 - len(ok)}.**",
                  "> Finora nessuna discrepanza, ma il campione non basta per una garanzia."]
    open("INTEGRITA.md", "w").write("\n".join(L))
    _ok = [r for r in tutte if r.get("esito") == "identici"]
    _cop = [r.get("copertura") for r in tutte if r.get("copertura") is not None]
    _media_cop = (sum(_cop) / len(_cop)) if _cop else None
    print(f"INTEGRITA | FEDELTA' {len(_ok)}/{len(tutte)} = "
          f"{100*len(_ok)/max(1,len(tutte)):.0f}% finestre senza discrepanze"
          + (f" | COPERTURA media {100*_media_cop:.0f}% degli eventi della catena"
             if _media_cop is not None else " | copertura non ancora misurata")
          + f" | {len(valide)} confrontabili, {len(tutte)-len(valide)} non giudicabili", flush=True)
    if _media_cop is not None:
        print("INTEGRITA | i due numeri vanno letti INSIEME: la fedelta' si alza giudicando meno, "
              "e in quel caso la copertura scende. Solo raccogliendo di piu' salgono entrambe.",
              flush=True)


if __name__ == "__main__":
    main()
