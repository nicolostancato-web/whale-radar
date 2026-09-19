"""BUCO — i pool del registro di cui non abbiamo una riga (si chiamava BUCO BASE).

VALE PER TUTTE E DUE LE CHAIN (19/09): si sceglie con CHAIN=base|robinhood. I limiti del nodo sono
diversi e misurati, non assunti: base accetta finestre da 2.000 blocchi e gruppi da 10, robinhood
20.000 e 100.

COME SONO STATI TROVATI (18/09). Scomponendo l'assenza di eventi, i 128 che mancavano davvero in
una finestra che falliva appartenevano TUTTI a pool per cui non avevamo un solo record: zero
cadeva in un tratto di blocchi che stavamo gia' leggendo. Non un archivio troncato: pool interi
mai cominciati.
Poi ho chiesto al nodo, per ognuno, se avesse mai scambiato. Su base: 101 id V4 su 102 SI', 40
indirizzi su 44 no (quelli sono voci sporche del registro, in quarantena). I 101 sono il buco vero.

PERCHE' LO SCAVO A FASCE NON LI PRENDE. Il collettore storico setaccia fasce di blocchi e tiene
quello che vi trova; quei pool sono nati fuori dalle fasce coperte finora, quindi nessuna pala e'
mai passata sopra la loro nascita. Aspettare che ci arrivi vuol dire aspettare che lo scavo copra
tutta la storia della chain — settimane, per 101 pool che sappiamo gia' nominare.
Qui si va DRITTI alla nascita di ognuno, che conosciamo dalla catena, e si prendono le sue prime
ore. E' l'unico agente che parte dai pool invece che dai blocchi.

GLI ISTANTI SONO VERI. I timestamp si chiedono al nodo per i blocchi che servono davvero, a
gruppi. Interpolare da un riferimento preso a inizio corsa e' quello che il 16/09 ha prodotto
istanti falsi fino a 84 minuti, e con essi una finestra di vita sbagliata per ogni pool.
"""
import gzip
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from storico_evm import SWAP_V2, SWAP_V3, SWAP_V4, firma, scarica_su_disco  # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
URL = {"base": "https://mainnet.base.org",
       "robinhood": "https://rpc.mainnet.chain.robinhood.com"}[CHAIN]
AMPIEZZA = 2000 if CHAIN == "base" else 20000   # misurato: base rifiuta oltre, con qualunque filtro
LOTTO = 10 if CHAIN == "base" else 100         # misurato: base rifiuta lotti piu' grandi con 413
ORE = float(os.environ.get("ORE_VITA", 8))
# secondi per blocco, misurati sulle due chain (servono a leggere l'arco del censimento)
SEC_BLOCCO = 2.0 if CHAIN == "base" else 0.106
BUDGET = int(os.environ.get("BUDGET_SEC", 900))
ELENCO = f"data/{CHAIN}_mai_letti.json"
# LE FETTE (19/09): il nodo limita per INDIRIZZO IP, misurato ieri sulle coppie (un filo 0,24
# pool/s, tre fili 0,22, sei fili zero). Da una macchina sola non si accelera. Ma ogni lavoro di
# GitHub ha un IP proprio: con 23.079 pool da prendere a ~60 secondi l'uno, una corsia sola impiega
# giorni e sei fette li dividono per sei.
FETTA = os.environ.get("FETTA")
N_FETTE = int(os.environ.get("N_FETTE", 6))
CK = (f"data/multichain/{CHAIN}/buco_ckpt_f{FETTA}.json" if FETTA is not None
      else f"data/multichain/{CHAIN}/buco_ckpt.json")


def mia(pool):
    """True se questo pool tocca a questa fetta. Senza fetta, tocca tutto a noi."""
    if FETTA is None:
        return True
    try:
        return int(pool[-6:], 16) % N_FETTE == int(FETTA)
    except Exception:
        return True
t0 = time.time()


def rpc(metodo, params, to=60):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    for k in range(3):
        try:
            r = urllib.request.Request(URL, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=to) as x:
                d = json.load(x)
            if "error" in d:
                return None, str(d["error"])[:60]
            return d.get("result"), None
        except Exception as e:
            if k < 2:
                time.sleep(2 * (k + 1))
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "esauriti"


def istanti(blocchi):
    """I timestamp veri dei blocchi chiesti, a gruppi. Mai interpolati."""
    fuori = {}
    b = sorted(blocchi)
    for i in range(0, len(b), LOTTO):
        gruppo = b[i:i + LOTTO]
        corpo = json.dumps([{"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                             "params": [hex(n), False], "id": n} for n in gruppo]).encode()
        try:
            r = urllib.request.Request(URL, data=corpo,
                                       headers={"Content-Type": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=60) as x:
                for d in json.load(x):
                    if d.get("result"):
                        fuori[int(d["result"]["number"], 16)] = int(d["result"]["timestamp"], 16)
        except Exception:
            pass
        time.sleep(0.2)
    return fuori


def main():
    # I BERSAGLI SI CALCOLANO OGNI VOLTA, NON SI LEGGONO DA UNA LISTA FISSA (19/09).
    # La prima versione leggeva i 105 pool di un elenco scritto a mano il giorno prima. Li ha presi
    # tutti — e il giorno dopo ce n'erano ALTRI 66, con la stessa identica malattia: nel registro,
    # mai raccolti, e vecchi fino a 900 ore. Controllati uno per uno: 25 su 25 sono POOL VERI, non
    # voci sporche. Il buco non era un incidente chiuso: e' una falla che si riapre, perche' il
    # registro cresce di continuo e lo scavo a fasce non passa dove quei pool sono nati.
    # Una lista fissa cura il sintomo una volta sola. Calcolare i bersagli a ogni giro cura la falla.
    # I BERSAGLI SONO LA POPOLAZIONE DEFINITA, NON SOLO IL REGISTRO (19/09).
    # Con le coppie finalmente risolte (base 98%, robinhood 100%) la definizione di DEFINIZIONE.md
    # si puo' finalmente APPLICARE, e dice che la popolazione da studiare e' 7.084 pool su base e
    # 15.995 su robinhood. Ne avevamo 228 e 227: il 3,2% e l'1,4%.
    # La condizione 1 del cancello chiede >=95% di QUELLA popolazione. Non ci si arriva raccogliendo
    # meglio i pool che gia' abbiamo: bisogna prendere gli altri ventiduemila.
    # Perche' proprio qui: questo agente parte dai POOL invece che dai blocchi, va dritto alla
    # nascita di ognuno e ne prende le prime ore. E' esattamente il lavoro che serve, gia' scritto e
    # gia' verificato contro la catena (istanti esatti al secondo, blockhash giusti, zero duplicati).
    # E IL CRITERIO NON GUARDA IL FUTURO. Si entra per «ha almeno 20 scambi nell'intervallo
    # dichiarato e ha una valuta di base da un lato»: entrambe cose vere al momento in cui si
    # decide. Il vecchio registro invece chiedeva almeno 5 candele e un minimo di volume — cioe'
    # ESSERE SOPRAVVISSUTI — ed escludeva cosi' il 52% dei pool proprio perche' erano andati male.
    # Quella e' la selezione che gonfia qualunque percentuale il loop 1 andra' a misurare.
    reg = {}
    try:
        reg = json.load(open(f"data/multichain/{CHAIN}/righe.json")).get("pool", {})
    except Exception:
        pass
    voluti = dict(reg)
    if os.environ.get("POPOLAZIONE", "1") == "1":
        try:
            basi = set(json.load(open("data/valute_base.json"))[CHAIN])
            cop = {k.lower(): v for k, v in
                   json.load(open(f"data/multichain/{CHAIN}/coppie.json")).get("coppie", {}).items()}
            n_pop = 0
            with gzip.open(f"data/multichain/{CHAIN}/censimento.jsonl.gz", "rt") as fo:
                for l in fo:
                    if not l.strip():
                        continue
                    d0 = json.loads(l)
                    if d0.get("scambi", 0) < 20:
                        continue
                    v = cop.get(d0["pool"])
                    if not v:
                        continue
                    t_0 = (v.get("t0") or "").lower()
                    t_1 = (v.get("t1") or "").lower()
                    if (t_0 in basi) == (t_1 in basi):
                        continue                  # o nessuno o entrambi: non e' la nostra popolazione
                    # QUANTO E' CONCENTRATA L'ATTIVITA' (19/09). Il censimento conta gli scambi su
                    # TUTTO l'intervallo dichiarato, che e' di settimane: un pool con 23 scambi
                    # sparsi su 1,4 milioni di blocchi soddisfa «>=20 scambi» ed e' un pool
                    # dormiente, non un evento. Misurato su sei pool a caso: quelli con arco stretto
                    # rendono 201 e 239 righe nelle prime ore, quelli con arco largo UNA.
                    # E qui c'e' la scoperta che conta: i pool che GIA' abbiamo sono in maggioranza
                    # i diluiti (14,2% di copertura), mentre dei concentrati abbiamo il 4,0%. Ha una
                    # causa — il vecchio registro sceglieva i sopravvissuti con almeno 5 candele,
                    # cioe' i longevi — e una conseguenza: il picco breve, che e' come si presenta
                    # una memecoin che pompa, nel nostro archivio quasi non c'e'.
                    # Non cambio la definizione (quella si registra in DEFINIZIONE.md, non si sposta
                    # in un agente): cambio l'ORDINE, e prendo prima quelli concentrati.
                    arco_ore = (d0.get("ultimo", 0) - d0.get("primo", 0)) * SEC_BLOCCO / 3600.0
                    voluti.setdefault(d0["pool"], {"ent": None, "t0": None,
                                                   "arco_ore": round(arco_ore, 2)})
                    n_pop += 1
            print(f"BUCO | {CHAIN}: popolazione definita {n_pop} pool "
                  f"(registro {len(reg)}, da cercare in tutto {len(voluti)})", flush=True)
        except Exception as e:
            print(f"BUCO | {CHAIN}: popolazione non leggibile ({type(e).__name__}), "
                  f"resto sul registro", flush=True)
    reg = voluti
    bersagli = []
    sporche = set()
    try:
        for x in json.load(open("data/quarantena_registro.json"))["non_sono_pool"].get(CHAIN, []):
            sporche.add(x.lower())
    except Exception:
        pass
    for p in reg:
        pl = p.lower()
        if pl in sporche:
            continue                      # gia' verificato che non e' un pool: non si ritenta
        # BASTA SAPERE SE IL FILE C'E', NON QUANTE RIGHE HA (19/09). Qui si aprivano e si
        # DECOMPRIMEVANO tutti i file per contarne le righe: con 8.778 bersagli vuol dire leggere
        # un centinaio di megabyte a ogni giro, e infatti il budget finiva nel censimento invece che
        # nella raccolta — un pool visitato in tre minuti. La domanda e' «di questo pool abbiamo
        # qualcosa?», e a quella risponde l'esistenza di un file non vuoto.
        if not mia(pl):
            continue
        if not any(os.path.exists(f"data/multichain/{CHAIN}/{c}/{pl}.jsonl.gz")
                   and os.path.getsize(f"data/multichain/{CHAIN}/{c}/{pl}.jsonl.gz") > 40
                   for c in ("storico", "vivo")):
            bersagli.append(pl)
    # l'elenco storico resta come semenza, se c'e' ancora qualcosa dentro che non abbiamo preso
    if os.path.exists(ELENCO):
        try:
            for p in json.load(open(ELENCO)).get("buco_vero", []):
                if p not in bersagli and p not in sporche:
                    bersagli.append(p)
        except Exception:
            pass
    # I CONCENTRATI PER PRIMI: rendono righe utili subito, i diluiti ne rendono una a testa.
    bersagli.sort(key=lambda p: (reg.get(p) or {}).get("arco_ore") or 1e9)
    if not bersagli:
        print(f"BUCO | {CHAIN}: nessun pool del registro e' senza righe. Niente da recuperare.",
              flush=True)
        return
    print(f"BUCO | {CHAIN}: {len(bersagli)} pool nel registro senza una riga", flush=True)
    nasc = {}
    try:
        for p, d in json.load(open(f"data/multichain/{CHAIN}/nascita_vera.json"))["nascite"].items():
            if d.get("fonte") == "catena" and (d.get("bn") or d.get("ts")):
                nasc[p.lower()] = d
    except Exception:
        pass
    punta, _ = rpc("eth_blockNumber", [])
    if not punta:
        print("BUCO | il nodo non risponde", flush=True)
        return
    punta = int(punta, 16)
    b1, _ = rpc("eth_getBlockByNumber", [hex(punta), False])
    b0, _ = rpc("eth_getBlockByNumber", [hex(punta - 100000), False])
    if not b1 or not b0:
        print("BUCO | non riesco a leggere il ritmo dei blocchi", flush=True)
        return
    ora = int(b1["timestamp"], 16)
    sec = (ora - int(b0["timestamp"], 16)) / 100000.0

    fatti = set()
    if os.path.exists(CK):
        try:
            fatti = set(json.load(open(CK)).get("fatti", []))
        except Exception:
            fatti = set()

    # dove il censimento ha visto ogni pool per la prima volta: e' l'ancora di ripiego
    primo_censimento = {}
    try:
        with gzip.open(f"data/multichain/{CHAIN}/censimento.jsonl.gz", "rt") as fo:
            for l in fo:
                if l.strip():
                    d0 = json.loads(l)
                    if d0.get("primo"):
                        primo_censimento[d0["pool"]] = int(d0["primo"])
    except Exception:
        pass

    per_pool = {}
    presi = saltati = 0
    for pool in bersagli:
        if time.time() - t0 > BUDGET:
            break
        if pool in fatti:
            continue
        d = nasc.get(pool)
        if not d:
            # L'ANCORA DI RIPIEGO VIENE DAL CENSIMENTO (19/09). Senza, questo agente saltava 6.434
            # bersagli su 6.536: la nascita risolta dalla catena ce l'ha solo il vecchio registro, e
            # la popolazione definita e' fatta quasi tutta di pool che il registro non ha mai visto.
            # Il censimento pero' sa in quale blocco li ha visti scambiare la PRIMA VOLTA dentro
            # l'intervallo dichiarato. Non e' la nascita — se il pool e' nato prima dell'intervallo,
            # il suo vero inizio e' altrove — ma e' un punto di partenza onesto, e le righe raccolte
            # cosi' vengono marcate «ancora: censimento» invece di spacciarsi per nascita.
            # nascita_vera.py potra' raffinarle dopo; intanto i dati entrano, invece di non entrare.
            b0 = primo_censimento.get(pool)
            if not b0:
                saltati += 1
                continue
            d = {"bn": b0, "ripiego": True}
        # la nascita in blocchi: quella dichiarata se c'e', altrimenti dal suo istante vero
        bn0 = int(d["bn"]) if d.get("bn") else int(punta - (ora - int(d["ts"])) / max(0.01, sec))
        fine = bn0 + int(ORE * 3600 / max(0.01, sec))
        righe = []
        cur = bn0
        while cur < fine and time.time() - t0 < BUDGET:
            a = min(fine, cur + AMPIEZZA)
            f = {"fromBlock": hex(cur), "toBlock": hex(a)}
            if len(pool) == 66:
                f["topics"] = [SWAP_V4, pool]
            else:
                f["address"] = pool
                f["topics"] = [[SWAP_V2, SWAP_V3, SWAP_V4]]
            log, err = rpc("eth_getLogs", [f])
            if log is None:
                break
            righe.extend(log)
            cur = a + 1
            time.sleep(0.15)
        if not righe:
            fatti.add(pool)
            continue
        ts = istanti({int(l["blockNumber"], 16) for l in righe})
        for l in righe:
            bn = int(l["blockNumber"], 16)
            if bn not in ts:
                continue                      # senza istante vero non si scrive: meglio mancante
            fi = firma(l["topics"][0], l.get("data", "0x"), l["topics"])
            if not fi:
                continue
            per_pool.setdefault(pool, []).append(
                {"acq": int(time.time()), "ts": ts[bn], "blocco": bn,
                 "tx": l.get("transactionHash"), "bh": l.get("blockHash"),
                 "ti": int(l.get("transactionIndex", "0x0"), 16),
                 "li": int(l.get("logIndex", "0x0"), 16),
                 "classe": "recupero-buco",
                 "ancora": "censimento" if d.get("ripiego") else "nascita", "w": fi["w"], "w_sem": fi.get("w_sem"),
                 "a0": fi["a0"], "a1": fi["a1"], "dex": fi["v"],
                 "mgr": l.get("address", "").lower(), "fonte": "catena"})
        fatti.add(pool)
        presi += 1

    nuovi = scarica_su_disco(CHAIN, per_pool) if per_pool else 0
    try:
        os.makedirs(os.path.dirname(CK), exist_ok=True)
        json.dump({"fatti": sorted(fatti), "quando": int(time.time())}, open(CK, "w"))
    except Exception:
        pass
    print(f"BUCO | {presi} pool visitati, {nuovi} righe nuove scritte | "
          f"{len(fatti)}/{len(bersagli)} dell'elenco chiusi"
          + (f" | {saltati} senza nascita dalla catena: non li tocco" if saltati else ""), flush=True)


if __name__ == "__main__":
    main()
