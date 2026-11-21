"""SCOPRITORE — chiede alla catena quali pool nascono, invece di chiederlo a un'API.

IL PROBLEMA CHE RISOLVE (16/09, la scoperta piu' importante finora). Il nostro registro dei pool
nasceva da un'API di terze parti che impiega ORE o GIORNI a elencare un pool nuovo. Ma noi teniamo
le **prime 6 ore di vita** di ogni pool. Venivamo a sapere che un pool esisteva DOPO che quelle sei
ore erano passate: stavamo sistematicamente mancando esattamente la finestra che dicevamo di
studiare.

Misurato sui pool con almeno 100 scambi che ci mancavano, di cui ho trovato la nascita:
    nati meno di 6 ore fa   109  (56%)   <- li abbiamo persi mentre accadevano
    nati 6-24 ore fa         41  (21%)
    nati 1-3 giorni fa       11  ( 6%)
    nati piu' di 3 giorni fa 34  (17%)   <- questi non li avremmo visti mai
Su 362 pool con >=100 scambi, ne avevamo 28. I due piu' scambiati che ci mancavano avevano 83.065
e 81.150 scambi.

E nessuno dei nostri indicatori poteva dirlo, perche' misuravano tutti il NOSTRO registro: il 97%,
il 65%, il 27% dell'audit erano tutti calcolati su un universo che ci eravamo scelti da soli.

COME. Ogni pool Uniswap V4 emette `Initialize` quando nasce, coi due token nei topics. E' l'unico
annuncio che non dipende da nessuno: se il pool esiste, quell'evento c'e'. Firma trovata sul campo:
    0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438

PERCHE' SOLO I NUOVI NATI. Sulla catena esistono 660.830 pool V4. Seguirli tutti non ha senso: la
stragrande maggioranza non ha mai scambiato, e di quelli vecchi le prime sei ore sono comunque
passate — quelle le recupera il backfill, se valgono. Qui interessano i pool che nascono ADESSO,
perche' sono gli unici di cui possiamo ancora prendere la nascita mentre succede.
Un universo grande non e' un universo utile: e' solo un universo grande.
"""
import gzip
import json
import os
import time
import urllib.request

INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
RPC = {"base": ("https://mainnet.base.org", 2.0, 2000),
       "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 0.1, 20000)}
CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = int(os.environ.get("BUDGET_SEC", 600))
PAUSA = float(os.environ.get("PAUSA", 1.0))
CK = f"data/multichain/{CHAIN}/scopritore_ckpt.json"
OUT = f"data/multichain/{CHAIN}/universo.jsonl.gz"
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
                return None, str(d["error"])[:70]
            return d.get("result"), None
        except Exception as e:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "tentativi esauriti"


def gia_noti():
    noti = set()
    if os.path.exists(OUT):
        try:
            for l in gzip.open(OUT, "rt"):
                if l.strip():
                    try:
                        noti.add(json.loads(l)["pool"])
                    except Exception:
                        pass
        except Exception:
            pass
    return noti


def main():
    url, sec_blocco, ampiezza = RPC.get(CHAIN, (None, None, None))
    if not url:
        print(f"SCOPRITORE | {CHAIN}: nessun nodo", flush=True)
        return
    punta, err = rpc(url, "eth_blockNumber", [])
    if not punta:
        print(f"SCOPRITORE | {CHAIN}: il nodo non risponde ({err})", flush=True)
        return
    punta = int(punta, 16)

    ck = {}
    if os.path.exists(CK):
        try:
            ck = json.load(open(CK))
        except Exception:
            ck = {}
    # SI PARTE DA UN GIORNO FA, NON DALL'INIZIO DELLA CATENA. Un pool nato ieri ha ancora senso:
    # le sue prime sei ore le possiamo ricostruire. Uno nato un mese fa no, e non serve a questo
    # raccoglitore — quello e' mestiere del backfill.
    un_giorno = int(86400 / sec_blocco)
    cursore = int(ck.get("ultimo") or (punta - un_giorno))
    if punta - cursore > un_giorno * 3:
        cursore = punta - un_giorno            # troppo indietro: il resto non e' piu' «nuovo»

    noti = gia_noti()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    nuovi = []
    chiamate = 0
    while time.time() - t0 < BUDGET and cursore < punta:
        a = min(punta, cursore + ampiezza)
        log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(cursore + 1), "toBlock": hex(a),
                                             "topics": [INIT]}])
        chiamate += 1
        if log is None:
            if ampiezza > 500:
                ampiezza //= 2                 # denso: si stringe, non si salta
                continue
            print(f"SCOPRITORE | blocchi {cursore + 1}-{a} illeggibili: LI STO SALTANDO ({err})",
                  flush=True)
            cursore = a
            time.sleep(PAUSA)
            continue
        # l'istante vero dei due estremi, per non ereditare il difetto dell'orario stimato
        bd, _1 = rpc(url, "eth_getBlockByNumber", [hex(cursore + 1), False])
        ba, _2 = rpc(url, "eth_getBlockByNumber", [hex(a), False])
        chiamate += 2
        t_lo = int(bd["timestamp"], 16) if bd else None
        t_hi = int(ba["timestamp"], 16) if ba else None
        for l in log:
            tp = l.get("topics") or []
            if len(tp) < 4:
                continue
            pid = tp[1].lower()
            if pid in noti:
                continue
            bn = int(l["blockNumber"], 16)
            if t_lo is not None and t_hi is not None and a > cursore + 1:
                ts = int(t_lo + (t_hi - t_lo) * (bn - cursore - 1) / (a - cursore - 1))
            else:
                ts = t_lo
            nuovi.append({"acq": int(time.time()), "pool": pid, "nato": bn, "ts": ts,
                          "t0": "0x" + tp[2][-40:], "t1": "0x" + tp[3][-40:],
                          "dex": 4, "fonte": "evento-creazione"})
            noti.add(pid)
        cursore = a
        time.sleep(PAUSA)

    if nuovi:
        try:
            with gzip.open(OUT, "at") as f:
                for r in sorted(nuovi, key=lambda x: x["nato"]):
                    f.write(json.dumps(r) + "\n")
        except Exception as e:
            print(f"SCOPRITORE | non sono riuscito a scrivere: {e}", flush=True)
    ck["ultimo"] = cursore
    ck["acq"] = int(time.time())
    try:
        json.dump(ck, open(CK, "w"))
    except Exception:
        pass
    indietro = (punta - cursore) * sec_blocco / 60
    print(f"SCOPRITORE | {CHAIN}: {chiamate} chiamate, {len(nuovi)} pool nuovi, "
          f"{len(noti)} nell'universo | sono indietro di {indietro:.0f} minuti dalla punta",
          flush=True)


if __name__ == "__main__":
    main()
