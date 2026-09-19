#!/usr/bin/env python3
"""
CODA_VIVA — l'unico dato che potra' essere certificato: quello preso mentre succede.

PERCHE' ESISTE (15/09). Il timbro di acquisizione ha appena misurato la verita' scomoda: il nostro
backfill ha un ritardo mediano di 362 ore su Base e 614 su Robinhood. Ovvio — raccoglie all'indietro
la storia di token nati settimane fa — ma significa che quei 147.000 record NON potranno mai essere
certificati point-in-time. Servono a esplorare, non a decidere.

Il dato su cui un verdetto vale e' solo quello raccolto MENTRE SUCCEDE. E nessuno lo stava
raccogliendo: le fette dello storico partono da adesso e vanno all'INDIETRO, quindi ogni blocco lo
vedono una volta sola e poi si allontanano. Un pool nato dieci minuti fa non viene ripreso da
nessuno.

Questa corsia fa il contrario: sta attaccata alla punta della catena e non si allontana mai. Ogni
giro legge i blocchi comparsi dall'ultimo giro, e basta. Il ritardo fra il fatto e il timbro resta
di minuti — ed e' quel numero, non una dichiarazione, che rendera' certificabile il dataset.

Non si puo' accelerare. Un giorno di dati certificati richiede un giorno. E' il vincolo vero del
progetto: non i soldi, non le API, il tempo che deve passare.

€0: nodi pubblici gratuiti.
"""
import json, gzip, os, time, urllib.request

SWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
SWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
SWAP_V4 = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
RPC = {"base": ("https://mainnet.base.org", 100), "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 400)}
CHAIN = os.environ.get("CHAIN", "base")
BUDGET = int(os.environ.get("BUDGET_SEC", 600))
PAUSA = float(os.environ.get("PAUSA", 1.4))
CK = f"data/multichain/{CHAIN}/coda_ckpt.json"
TETTO_POOL = int(os.environ.get("TETTO_POOL", 300))
SOGLIA_PIT = int(os.environ.get("SOGLIA_PIT", 900))        # oltre 15 minuti non e' piu' «mentre succedeva»
# L'ARRETRATO SI MISURA IN TEMPO, NON IN BLOCCHI (16/09, secondo giro di correzione). Prima era
# ventimila blocchi: su robinhood, che ne fa dieci al secondo, sono 33 minuti; su base, che ne fa
# uno ogni due secondi, sono UNDICI ORE. La stessa soglia scritta in blocchi vuol dire cose
# lontanissime su due chain diverse — ed e' lo stesso errore per cui non si puo' usare il ritardo
# di una chain per giudicarne un'altra.
# Qui l'unita' giusta e' quella della domanda: «quanto tempo fa e' successo?».
ARRETRATO_MAX_SEC = int(os.environ.get("ARRETRATO_MAX_SEC", 600))   # oltre dieci minuti, si salta
t0 = time.time()


def rpc(url, metodo, params, tentativi=3):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    attesa = 3
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=40) as x:
                d = json.load(x)
            if "error" in d: return None, str(d["error"])[:70]
            return d.get("result"), None
        except Exception as e:
            if k < tentativi - 1: time.sleep(attesa); attesa *= 2; continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "tentativi esauriti"


def scarica(chain, per_pool):
    """Svuota il raccolto sui file. Torna quante righe nuove ha scritto.

    IL TETTO VA RISPETTATO ANCHE QUI (16/09). Da quando la coda viva segue anche i pool nati nelle
    ultime 24 ore, i pool osservati sono passati da 118 a 406 e gli scambi raccolti da 950 a 11.576
    in ottanta secondi. E' esattamente quello che volevamo — ma senza tetto diventerebbe un archivio
    che cresce senza limite, e il peso del repo e' gia' stato un problema una volta.
    Di ogni pool teniamo al massimo TETTO_POOL scambi, come ovunque: il valore sta nelle prime ore
    di vita, non nel millesimo scambio del secondo giorno."""
    nuovi = 0
    for pool, righe in per_pool.items():
        p = f"data/multichain/{chain}/vivo/{pool}.jsonl.gz"
        visti = set()
        if os.path.exists(p):
            try:
                for l in gzip.open(p, "rt"):
                    if l.strip():
                        try:
                            d = json.loads(l); visti.add((d.get("tx"), d.get("li")))
                        except Exception: pass
            except Exception: pass
        if len(visti) >= TETTO_POOL:
            continue                            # pool gia' al tetto: non si aggiunge altro
        da = [r for r in righe if (r.get("tx"), r.get("li")) not in visti]
        da = da[:max(0, TETTO_POOL - len(visti))]
        if not da: continue
        try:
            with gzip.open(p, "at") as fo:
                for r in sorted(da, key=lambda x: (x["ts"], x.get("ti", 0), x.get("li", 0))):
                    fo.write(json.dumps(r) + "\n")
            nuovi += len(da)
        except Exception: pass
    return nuovi


def salva_e_spingi(etichetta):
    """Si salva strada facendo: un giro da due ore e mezza che muore non deve portarsi via due ore
    e mezza di blocchi che nessuno potra' piu' raccogliere."""
    import subprocess
    subprocess.run('git config user.name "whale-radar-bot"; git config user.email '
                   '"bot@users.noreply.github.com"', shell=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if subprocess.run(f'git add -A && git commit -m "vivo {etichetta}"', shell=True,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        return False
    for _ in range(8):
        subprocess.run('git pull --no-rebase --no-edit -X ours origin main', shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.run('git push origin main', shell=True,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return True
        time.sleep(6)
    print("CODA_VIVA | ATTENZIONE: non sono riuscito a spingere", flush=True)
    return False


def main():
    url, ampiezza = RPC.get(CHAIN, (None, None))
    if not url:
        print(f"CODA_VIVA | {CHAIN} non e' una chain che sappiamo leggere"); return
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import storico_evm as S

    punta, err = rpc(url, "eth_blockNumber", [])
    if not punta:
        print(f"CODA_VIVA | il nodo non risponde: {err}"); return
    punta = int(punta, 16)
    try:
        ck = json.load(open(CK))
    except Exception:
        ck = {}
    # alla prima accensione si parte da POCO indietro: la coda viva non recupera il passato, quello
    # e' il mestiere delle fette. Qui conta solo restare attaccati alla punta.
    cursore = int(ck.get("ultimo") or (punta - ampiezza * 3))

    b_now, _ = rpc(url, "eth_getBlockByNumber", [hex(punta), False])
    b_pre, _ = rpc(url, "eth_getBlockByNumber", [hex(punta - 20000), False])
    if not b_now or not b_pre:
        print("CODA_VIVA | non riesco a fissare gli istanti"); return
    t_now = int(b_now["timestamp"], 16)
    sec_blocco = (t_now - int(b_pre["timestamp"], 16)) / 20000.0

    nostri = set()
    try:
        nostri = {k.lower() for k in json.load(open(f"data/multichain/{CHAIN}/righe.json")).get("pool", {})}
    except Exception:
        pass
    import glob as _g
    for d in ("candles", "pulse"):
        for f in _g.glob(f"data/multichain/{CHAIN}/{d}/*.jsonl.gz"):
            nostri.add(os.path.basename(f).replace(".jsonl.gz", "").lower())
    # I NUOVI NATI, PRESI DALLA CATENA (16/09). Finora questa lista veniva solo dalle candele, cioe'
    # da un'API di terze parti che impiega ore o giorni a elencare un pool nuovo — mentre noi
    # teniamo le PRIME SEI ORE di vita. Arrivavamo sempre dopo.
    # Misurato: nelle ultime 24 ore su robinhood sono nati 16.514 pool; il nostro registro ne
    # conosceva CINQUE. Lo scopritore li prende dall'evento di creazione, che esiste nell'istante
    # in cui il pool nasce e non dipende da nessuno.
    # Si tengono solo quelli nati nelle ultime 24 ore: degli altri le sei ore sono comunque passate,
    # e sono mestiere del backfill. La stragrande maggioranza non scambiera' mai, e non costa nulla:
    # chi non scambia non produce righe.
    uni = f"data/multichain/{CHAIN}/universo.jsonl.gz"
    if os.path.exists(uni):
        limite = time.time() - 86400
        quanti = 0
        try:
            for l in gzip.open(uni, "rt"):
                if not l.strip():
                    continue
                try:
                    d0 = json.loads(l)
                except Exception:
                    continue
                if d0.get("ts") and d0["ts"] >= limite and d0.get("pool") not in nostri:
                    nostri.add(d0["pool"])
                    quanti += 1
        except Exception:
            pass
        print(f"CODA_VIVA | {CHAIN}: +{quanti} pool nati nelle ultime 24 ore dalla catena", flush=True)

    os.makedirs(f"data/multichain/{CHAIN}/vivo", exist_ok=True)
    per_pool = {}
    chiamate = presi = 0
    ritardi = []
    ultimo_salvataggio = [time.time()]
    totale = [0]
    while time.time() - t0 < BUDGET:
        punta, _ = rpc(url, "eth_blockNumber", [])
        punta = int(punta, 16) if punta else cursore
        if cursore >= punta:
            time.sleep(5); continue                      # siamo in pari: si aspetta la catena
        # SE SI RESTA TROPPO INDIETRO SI SALTA ALLA PUNTA (16/09, misurato dopo due giri veri).
        # Questa corsia esiste per una cosa sola: prendere il fatto MENTRE succede. Il primo giro
        # dava 5,2 minuti di ritardo mediano; il secondo 67,6 su base e 53 su robinhood, perche' il
        # cursore aveva accumulato arretrato e lo rincorreva in ordine senza mai raggiungere la
        # punta. Un arretrato non si smaltisce restando in coda: si accumula.
        # Rincorrere qui e' la scelta sbagliata due volte. Quei blocchi il backfill li puo' rifare
        # domani con calma; il blocco di ADESSO, se lo perdi mentre rincorri, non torna piu'.
        # Quindi: si dichiara il buco, si salta alla punta, e si riprende a fare il proprio mestiere.
        if (punta - cursore) * sec_blocco > ARRETRATO_MAX_SEC:
            print(f"CODA_VIVA | {CHAIN}: ero indietro di {punta - cursore} blocchi "
                  f"(~{(punta - cursore) * sec_blocco / 60:.0f} min): SALTO ALLA PUNTA. "
                  f"I blocchi {cursore + 1}-{punta - ampiezza} li lascio al backfill.", flush=True)
            try:
                with open(f"data/multichain/{CHAIN}/vivo_buchi.jsonl", "a") as fb:
                    fb.write(json.dumps({"acq": int(time.time()), "da": cursore + 1,
                                         "a": punta - ampiezza}) + "\n")
            except Exception:
                pass
            cursore = punta - ampiezza
        a = min(punta, cursore + ampiezza)
        # L'ISTANTE SI ANCORA AL LOTTO, NON ALL'AVVIO (16/09, il difetto piu' grave trovato finora).
        # Prima ogni istante veniva interpolato da un riferimento (punta, ora) preso all'AVVIO del
        # giro. Quel riferimento invecchia insieme al giro: dopo un'ora, i blocchi appena presi
        # risultavano vecchi di mezz'ora. Misurato su un blocco vero: istante scritto 1789538007,
        # istante vero 1789539905 — SBAGLIATO DI 31,6 MINUTI.
        # Le conseguenze erano due, e la seconda e' peggiore della prima:
        #   1. il ritardo sembrava 21 minuti quando il VERO era ZERO, e declassavamo a
        #      «ricostruzione storica» record che erano point-in-time perfetti;
        #   2. il campo «ts» — l'orario su cui poggiano embargo, unioni e ogni analisi futura —
        #      conteneva un orario falso. Un ritardo sbagliato e' un indicatore sbagliato; un
        #      ORARIO sbagliato e' un dato sbagliato, e si propaga a tutto quello che ci costruisci.
        # Adesso si chiedono alla catena gli istanti veri dei due estremi del lotto e si interpola
        # solo DENTRO quei due — poche centinaia di blocchi, non milioni. Due chiamate in piu' per
        # lotto: e' il prezzo di avere un orario vero invece di uno plausibile.
        ts_da, _e1 = rpc(url, "eth_getBlockByNumber", [hex(cursore + 1), False])
        ts_a, _e2 = rpc(url, "eth_getBlockByNumber", [hex(a), False])
        chiamate += 2
        if ts_da and ts_a:
            t_lo, t_hi = int(ts_da["timestamp"], 16), int(ts_a["timestamp"], 16)
            b_lo, b_hi = cursore + 1, a
        else:
            t_lo = t_hi = b_lo = b_hi = None
        log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(cursore + 1), "toBlock": hex(a),
                                             "topics": [[SWAP_V2, SWAP_V3, SWAP_V4]]}])
        chiamate += 1
        if log is None:
            ampiezza = max(10, ampiezza // 2); time.sleep(3); continue
        adesso = int(time.time())
        for l in log:
            tp = l.get("topics") or []
            pool = (tp[1].lower() if (tp and tp[0] == SWAP_V4 and len(tp) > 1) else l["address"].lower())
            if pool not in nostri: continue
            f = S.firma(tp[0], l.get("data", "0x"), tp)
            if not f: continue
            bn = int(l["blockNumber"], 16)
            if t_lo is not None and t_hi is not None and b_hi > b_lo:
                ts = int(t_lo + (t_hi - t_lo) * (bn - b_lo) / (b_hi - b_lo))
            elif t_lo is not None and t_hi is None:
                ts = t_lo
            else:
                ts = int(t_now - (punta - bn) * sec_blocco)   # solo se il nodo non risponde
            ritardi.append(adesso - ts)
            per_pool.setdefault(pool, []).append(
                {"acq": adesso, "ts": ts, "blocco": bn, "tx": l.get("transactionHash"),
                 "bh": l.get("blockHash"), "ti": int(l.get("transactionIndex", "0x0"), 16),
                 "li": int(l.get("logIndex", "0x0"), 16),
                 # L'ETICHETTA LA DECIDE IL RITARDO MISURATO, NON L'INTENZIONE (16/09). Marcavo
                 # ogni record «point-in-time» perche' veniva da questa corsia. Ma quando la corsia
                 # e' rimasta indietro di 67 minuti, quei record portavano scritto addosso
                 # esattamente la cosa che stiamo cercando di certificare — ed era falsa.
                 # Un dato che si auto-dichiara buono e' peggio di un dato senza etichetta.
                 "classe": ("point-in-time" if (adesso - ts) <= SOGLIA_PIT
                            else "ricostruzione-storica"),
                 "ritardo": adesso - ts,            # scritto dentro: chi analizza non deve fidarsi
                 "w": f["w"], "w_sem": f.get("w_sem"), "a0": f["a0"], "a1": f["a1"],
                 "dex": f["v"], "mgr": l.get("address", "").lower(), "fonte": "catena-viva"})
            presi += 1
        cursore = a
        if time.time() - ultimo_salvataggio[0] > 600:      # ogni dieci minuti si mette al sicuro
            n_ = scarica(CHAIN, per_pool); totale[0] += n_
            per_pool.clear()
            try: json.dump({"ultimo": cursore, "acq": int(time.time())}, open(CK, "w"))
            except Exception: pass
            salva_e_spingi(f"{CHAIN} +{n_} {time.strftime('%H:%MZ', time.gmtime())}")
            ultimo_salvataggio[0] = time.time()
        time.sleep(PAUSA)

    nuovi = scarica(CHAIN, per_pool) + totale[0]
    try:
        json.dump({"ultimo": cursore, "acq": int(time.time())}, open(CK, "w"))
    except Exception: pass
    try:
        import registro_pit as R
        R.annota("coda_viva", "catena-viva", CHAIN, nuovi, {"chiamate": chiamate})
    except Exception: pass
    import statistics as st
    med = st.median(ritardi) if ritardi else None
    print(f"CODA_VIVA | {CHAIN}: {chiamate} chiamate, {presi} swap nostri, {nuovi} nuovi, "
          f"{len(per_pool)} pool | ritardo mediano "
          + (f"{med/60:.1f} minuti" if med is not None else "n/d"), flush=True)


if __name__ == "__main__":
    main()
