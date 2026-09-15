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
        grezzi = []
        for cartella in ("storico", "vivo"):
            for f in glob.glob(f"data/multichain/{chain}/{cartella}/*.gz")[:400]:
                pool_f = os.path.basename(f).replace(".jsonl.gz", "").lower()
                try:
                    for l in gzip.open(f, "rt"):
                        if l.strip():
                            d0 = json.loads(l)
                            if d0.get("blocco") and d0.get("ts"):
                                grezzi.append((pool_f, d0["blocco"], d0["ts"]))
                except Exception: pass
        if len(grezzi) < 50: continue
        # la nascita di ogni pool: serve a sapere quali scambi avevamo DECISO di tenere
        nascita = {}
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
            # LA CATENA GREZZA, senza nessuno dei nostri filtri: serve per la domanda
            # «ce lo siamo inventato?», che e' diversa da «ci manca qualcosa?».
            grezza = set()
            for l in log:
                tp = l.get("topics") or []
                pl = (tp[1].lower() if (tp and tp[0] == V4 and len(tp) > 1) else l["address"].lower())
                if pl in nostri:
                    grezza.add((l.get("transactionHash"), int(l.get("logIndex", "0x0"), 16)))
            casa = nostri_record(chain, da, a, nostri)
            # E SI ESCLUDONO I POOL AL TETTO (15/09). Teniamo al massimo 300 scambi per pool: per
            # quelli arrivati al tetto la catena ne ha di piu' PER FORZA, ed e' una nostra scelta.
            # Confrontarli sarebbe misurare di nuovo le nostre decisioni chiamandole guasti.
            # Ogni regola di conservazione che aggiungiamo va replicata QUI, altrimenti il controllo
            # di integrita' diventa un generatore di falsi allarmi — e un allarme che suona sempre
            # e' un allarme che nessuno guarda.
            al_tetto = set()
            for pool in set(catena.values()):
                n_tot = 0
                for cart in ("storico", "vivo"):
                    f2 = f"data/multichain/{chain}/{cart}/{pool}.jsonl.gz"
                    if os.path.exists(f2):
                        try: n_tot += sum(1 for l in gzip.open(f2, "rt") if l.strip())
                        except Exception: pass
                if n_tot >= int(os.environ.get("TETTO_POOL", 300)): al_tetto.add(pool)
            catena = {k: v for k, v in catena.items() if v not in al_tetto}
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
                          "mancanti": len(mancanti), "inventati": len(inventati), "esito": esito,
                          "conversione": conversione(chain),
                          "pool_senza_nascita": len(senza_nascita), "prima_di_noi": prima_di_noi})

    if nuove:
        try:
            with open(REG, "a") as f:
                for r in nuove: f.write(json.dumps(r) + "\n")
        except Exception: pass
    righe += nuove

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
    print(f"INTEGRITA | {len(valide)} finestre valide, {len(ok)} identiche, "
          f"{len(valide) - len(ok)} discrepanze", flush=True)


if __name__ == "__main__":
    main()
