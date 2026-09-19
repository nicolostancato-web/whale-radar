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
BUDGET = int(os.environ.get("BUDGET_SEC", 900))
ELENCO = f"data/{CHAIN}_mai_letti.json"
CK = f"data/multichain/{CHAIN}/buco_ckpt.json"
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
    bersagli = []
    reg = {}
    try:
        reg = json.load(open(f"data/multichain/{CHAIN}/righe.json")).get("pool", {})
    except Exception:
        pass
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
        righe = 0
        for cart in ("storico", "vivo"):
            f = f"data/multichain/{CHAIN}/{cart}/{pl}.jsonl.gz"
            if os.path.exists(f):
                try:
                    righe += sum(1 for l in gzip.open(f, "rt") if l.strip())
                except Exception:
                    pass
            if righe:
                break
        if not righe:
            bersagli.append(pl)
    # l'elenco storico resta come semenza, se c'e' ancora qualcosa dentro che non abbiamo preso
    if os.path.exists(ELENCO):
        try:
            for p in json.load(open(ELENCO)).get("buco_vero", []):
                if p not in bersagli and p not in sporche:
                    bersagli.append(p)
        except Exception:
            pass
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

    per_pool = {}
    presi = saltati = 0
    for pool in bersagli:
        if time.time() - t0 > BUDGET:
            break
        if pool in fatti:
            continue
        d = nasc.get(pool)
        if not d:
            saltati += 1
            continue
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
                 "classe": "recupero-buco", "w": fi["w"], "w_sem": fi.get("w_sem"),
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
