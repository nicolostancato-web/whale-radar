"""CENSIMENTO — l'universo vero: ogni pool che ha SCAMBIATO in un intervallo dichiarato.

PERCHE' QUELLO DI PRIMA NON ANDAVA (17/09, rilievo della revisione esterna). L'«universo
indipendente» era costruito dall'evento `Initialize`, che esiste solo per i pool Uniswap V4.
Misurato dopo il rilievo:

    universo base:       8.123 pool, di cui con indirizzo (V2/V3):  ZERO
    universo robinhood: 29.773 pool, di cui con indirizzo (V2/V3):  ZERO
    pool del NOSTRO registro assenti da quell'universo: 1.910 su 1.925 (base)
                                                          777 su   796 (robinhood)

Non era l'universo della chain: era la lista dei pool V4 nati di recente. E ci avevamo costruito
sopra tre cose — la «copertura vera» allo 0,1%, la classificazione delle esclusioni, e il confronto
che accusava di autoreferenzialita' il 97%.
Cioe': il mio universo indipendente era autoreferenziale a sua volta, solo in un modo diverso. Non
selezionava col nostro filtro, selezionava col filtro di UNA VERSIONE DI PROTOCOLLO.

LA VIA D'USCITA. Ogni pool che ha mai scambiato ha emesso un log di swap, quale che sia la sua
versione. Un censimento costruito dai log di swap e' COMPLETO PER COSTRUZIONE per tutto cio' che
conta, e i pool che non hanno mai scambiato non ci interessano comunque: non producono righe, non
producono prezzi, non producono niente.

L'INTERVALLO SI DICHIARA PRIMA DI GUARDARE. Il censimento vale per un intervallo di altezze scritto
nel file, non «la catena». Cosi' chiunque puo' rifarlo e ottenere lo stesso risultato, e nessuna
percentuale calcolata su di esso puo' spacciarsi per «tutta la chain».

COSA SCRIVE per ogni pool: il primo e l'ultimo blocco in cui l'abbiamo visto scambiare dentro
l'intervallo, e quanti scambi. Chi analizza puo' quindi filtrare per attivita' senza chiedere altro.
"""
import gzip
import json
import os
import time
import urllib.request

SWAP = ["0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
        "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67",
        "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"]
V4 = SWAP[2]
RPC = {"base": ("https://mainnet.base.org", 400),
       "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 1000)}
CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = int(os.environ.get("BUDGET_SEC", 600))
GIORNI = float(os.environ.get("GIORNI", 3))       # quanto indietro va l'intervallo dichiarato
CK = f"data/multichain/{CHAIN}/censimento_ckpt.json"
OUT = f"data/multichain/{CHAIN}/censimento.jsonl.gz"
t0 = time.time()


def rpc(url, metodo, params, tentativi=4, to=90):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    attesa = 4
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=to) as x:
                d = json.load(x)
            if "error" in d:
                return None, str(d["error"])[:60]
            return d.get("result"), None
        except Exception as e:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "esauriti"


def main():
    url, ampiezza = RPC.get(CHAIN, (None, None))
    if not url:
        print(f"CENSIMENTO | {CHAIN}: nessun nodo", flush=True)
        return
    punta, err = rpc(url, "eth_blockNumber", [])
    if not punta:
        print(f"CENSIMENTO | {CHAIN}: il nodo non risponde ({err})", flush=True)
        return
    punta = int(punta, 16)

    ck = {}
    if os.path.exists(CK):
        try:
            ck = json.load(open(CK))
        except Exception:
            ck = {}

    # L'INTERVALLO SI FISSA UNA VOLTA E NON SI MUOVE. Se lo ricalcolassi a ogni giro seguendo la
    # punta, il censimento non finirebbe mai e il denominatore cambierebbe sotto i piedi a chi lo
    # usa — lo stesso difetto per cui la copertura «saliva mentre la realta' peggiorava».
    # UN INTERVALLO FINITO NE DICHIARA UN ALTRO (18/09). Il censimento di base ha completato il suo
    # intervallo e da allora il suo giro dura CINQUE SECONDI: la guardia del riarmo — nata per
    # impedire a un giro rotto di rilanciarsi all'infinito — lo ha letto come un guasto e ha
    # spento la corsia per quattro ore.
    # Ma «non ho niente da fare» e «sono rotto» sono due cose diverse, e la differenza qui e'
    # sostanziale: un censimento di tre giorni fermi invecchia. Il mercato di tre giorni fa non e'
    # quello di adesso, e il denominatore deve restare vivo quanto il numeratore.
    # Quindi quando un intervallo chiude se ne dichiara uno nuovo, che parte dove finiva il
    # precedente e arriva alla punta. Gli intervalli restano scritti uno per uno: nessuno si
    # sovrappone, nessuno si perde, e si puo' sempre dire di quale periodo parla un numero.
    if ck.get("da") and ck.get("a") and int(ck.get("cur", ck["a"])) <= ck["da"]:
        vecchio = f"{ck['da']}-{ck['a']}"
        storia = ck.get("chiusi", [])
        storia.append(vecchio)
        nuovo_da = ck["a"] + 1
        if punta > nuovo_da + 1000:
            ck = {"da": nuovo_da, "a": punta, "cur": punta, "chiusi": storia,
                  "dichiarato_il": int(time.time())}
            print(f"CENSIMENTO | {CHAIN}: intervallo {vecchio} CHIUSO. "
                  f"Ne dichiaro uno nuovo: {nuovo_da}-{punta}", flush=True)
        else:
            print(f"CENSIMENTO | {CHAIN}: intervallo {vecchio} chiuso e la catena non e' ancora "
                  f"avanzata abbastanza. Aspetto.", flush=True)
            ck["cur"] = ck["da"]
            try:
                json.dump(ck, open(CK, "w"))
            except Exception:
                pass
            return
    if not ck.get("da") or not ck.get("a"):
        b_now, _ = rpc(url, "eth_getBlockByNumber", [hex(punta), False])
        b_pre, _ = rpc(url, "eth_getBlockByNumber", [hex(max(1, punta - 20000)), False])
        if not b_now or not b_pre:
            print(f"CENSIMENTO | {CHAIN}: non riesco a stimare il ritmo dei blocchi", flush=True)
            return
        sec_b = (int(b_now["timestamp"], 16) - int(b_pre["timestamp"], 16)) / 20000.0
        larghezza = int(GIORNI * 86400 / max(0.01, sec_b))
        ck["da"] = max(1, punta - larghezza)
        ck["a"] = punta
        ck["cur"] = ck["a"]
        ck["dichiarato_il"] = int(time.time())
        print(f"CENSIMENTO | {CHAIN}: intervallo DICHIARATO {ck['da']}-{ck['a']} "
              f"({larghezza} blocchi ~ {GIORNI} giorni, {sec_b:.2f}s per blocco)", flush=True)

    noti = {}
    if os.path.exists(OUT):
        try:
            for l in gzip.open(OUT, "rt"):
                if l.strip():
                    d = json.loads(l)
                    noti[d["pool"]] = d
        except Exception:
            pass

    cur = int(ck.get("cur") or ck["a"])
    chiamate = 0
    visti = {}
    while cur > ck["da"] and time.time() - t0 < BUDGET:
        da = max(ck["da"], cur - ampiezza)
        log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(cur),
                                             "topics": [SWAP]}])
        chiamate += 1
        if log is None:
            if ampiezza > 50:
                ampiezza = max(50, ampiezza // 2)
                continue                      # si stringe, non si salta
            print(f"CENSIMENTO | blocchi {da}-{cur} illeggibili: LI STO SALTANDO ({err})",
                  flush=True)
            cur = da - 1
            continue
        for l in log:
            tp = l.get("topics") or []
            pool = (tp[1].lower() if (tp and tp[0] == V4 and len(tp) > 1)
                    else l["address"].lower())
            bn = int(l["blockNumber"], 16)
            v = visti.setdefault(pool, {"pool": pool, "primo": bn, "ultimo": bn, "scambi": 0,
                                        "tipo": "id" if len(pool) == 66 else "indirizzo"})
            v["primo"] = min(v["primo"], bn)
            v["ultimo"] = max(v["ultimo"], bn)
            v["scambi"] += 1
        cur = da - 1
        ck["cur"] = cur
        time.sleep(0.25)

    # si fondono con quelli gia' noti: il censimento cresce, non si riscrive
    for p, v in visti.items():
        w = noti.get(p)
        if w:
            w["primo"] = min(w["primo"], v["primo"])
            w["ultimo"] = max(w["ultimo"], v["ultimo"])
            w["scambi"] = w.get("scambi", 0) + v["scambi"]
        else:
            v["acq"] = int(time.time())
            v["intervallo"] = f"{ck['da']}-{ck['a']}"
            noti[p] = v
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    try:
        with gzip.open(OUT, "wt") as f:
            for v in sorted(noti.values(), key=lambda x: -x["scambi"]):
                f.write(json.dumps(v) + "\n")
    except Exception as e:
        print(f"CENSIMENTO | non sono riuscito a scrivere: {e}", flush=True)
    try:
        json.dump(ck, open(CK, "w"))
    except Exception:
        pass

    fatto = 100 * (ck["a"] - cur) / max(1, ck["a"] - ck["da"])
    idv = sum(1 for v in noti.values() if v["tipo"] == "id")
    ind = sum(1 for v in noti.values() if v["tipo"] == "indirizzo")
    print(f"CENSIMENTO | {CHAIN}: {chiamate} chiamate, intervallo al {fatto:.0f}% | "
          f"{len(noti)} pool che hanno scambiato ({idv} con id, {ind} con indirizzo)", flush=True)
    if fatto >= 99.9:
        print(f"CENSIMENTO | {CHAIN}: INTERVALLO COMPLETO. Questo e' l'universo dei pool che hanno "
              f"scambiato fra i blocchi {ck['da']} e {ck['a']}, e nient'altro.", flush=True)


if __name__ == "__main__":
    main()
