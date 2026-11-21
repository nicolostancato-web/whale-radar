"""IL REGISTRO DELLE DIPLOMATE, dalla chain e non da cio' che abbiamo visto per caso.

== PERCHE' (8/10/2026) ==

Il nostro `coppie.json` copre **un pool su dodici**: su 150 lanci casuali, 12 avevano un pool (il
tasso di diploma vero e' l'**8%**, non lo 0,77% che ho ripetuto per giorni) e solo 1 era nel
registro.

Conseguenza grave: ogni misura sul mercato dopo il diploma e' stata fatta su un campione estratto
da quel registro, che contiene i pool che i nostri raccoglitori hanno **visto scambiare** — cioe'
i piu' attivi. Il +18,9% della regola senza selezione e' quindi **sospetto di selezione**.

Qui il registro si costruisce dalla chain, per qualunque moneta, in tre passi:
  1. il gettone ha trasferito qualcosa al **gestore dei pool** di Uniswap v4? -> si e' diplomato;
  2. in quella transazione c'e' l'evento **Initialize**, che porta l'id del pool in `topics[1]`;
  3. con l'id si leggono tutti gli scambi di quel pool, in una chiamata.

Cosi' un campione di diplomate e' **casuale sul mondo**, non casuale su quello che avevamo visto.
"""
import gzip
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as CP                                      # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
ARCH = f"{BASE}/diplomate_vere.jsonl"
GESTORE_V4 = os.environ.get("GESTORE_V4", "0x8366a39cc670b4001a1121b8f6a443a643e40951").lower()
TRASF = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
INIT8 = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
INIT6 = "0x3fd553db44f207b1f41348cfc4d251860814af9eadc470e8e7895e4d120511f4"
QUANTE = int(os.environ.get("QUANTE", "400"))
BUDGET = int(os.environ.get("BUDGET_SEC", "2500"))
SEME = int(os.environ.get("SEME", "41"))


def pool_di(tok, nato, bn):
    """(poolId, blocco del diploma) se la moneta ha graduato. None se la chain non risponde."""
    pad = "0x" + "0" * 24 + GESTORE_V4[2:]
    r = CP.chiama("eth_getLogs", [{"fromBlock": hex(nato), "toBlock": hex(min(bn, nato + 9999999)),
                                   "address": tok, "topics": [TRASF, None, pad]}])
    if r is None:
        return None
    if not r:
        return ("mai", None)
    h = sorted(r, key=lambda x: int(x["blockNumber"], 16))[0]["transactionHash"]
    ric = CP.chiama("eth_getTransactionReceipt", [h])
    if not ric:
        return None
    for l in ric.get("logs", []):
        t = (l.get("topics") or [None])[0]
        if t in (INIT8, INIT6) and len(l["topics"]) > 1:
            return (l["topics"][1].lower(), int(l["blockNumber"], 16))
    # nessun Initialize nella transazione del primo trasferimento: il pool esiste ma l'id no.
    # Lo si dichiara invece di inventarlo: senza id non si leggono gli scambi.
    return ("senza id", int(ric["blockNumber"], 16))


def main():
    # UNA SOLA LIBRERIA DI LETTURA (10/10, prescrizione di Astra). Questo file era un
    # oggetto unico da 52 MB con 675.145 voci: per aggiungere un lancio si riscriveva
    # tutto. Ora sta a righe, e `archivio.leggi` nasconde quale forma c'e': se un giorno
    # cambia di nuovo, cambia li' e non in dieci script con dieci interpretazioni.
    import archivio as AR
    _test, _voci = AR.leggi("curva_lanci")
    dl = dict(_test)
    dl["da"] = _voci
    L = dl["da"]
    random.seed(SEME)
    camp = random.sample(sorted(L), QUANTE)
    fatte = set()
    if os.path.exists(ARCH):
        for l in open(ARCH):
            if l.strip():
                try:
                    fatte.add(json.loads(l)["moneta"])
                except Exception:
                    pass
    bn = int(CP.chiama("eth_blockNumber", []) or "0x0", 16)
    if not bn:
        print("DIPLOMATE | la chain non risponde.")
        return 0
    t0 = time.time()
    n = dip = senza = 0
    with open(ARCH, "a", buffering=1) as f:
        for tok in camp:
            if tok in fatte:
                continue
            if time.time() - t0 > BUDGET:
                print("DIPLOMATE | finito il tempo: l'archivio resta.", flush=True)
                break
            v = pool_di(tok, L[tok]["blocco"], bn)
            if v is None:
                continue              # lettura incompleta: non si scrive e si riprova
            pid, blocco = v
            n += 1
            if pid == "mai":
                f.write(json.dumps({"moneta": tok, "diplomata": 0}) + "\n")
            else:
                dip += 1
                if pid == "senza id":
                    senza += 1
                f.write(json.dumps({"moneta": tok, "diplomata": 1, "pool": pid,
                                    "blocco_diploma": blocco,
                                    "nato": L[tok]["blocco"]}) + "\n")
            time.sleep(0.2)
            if n % 50 == 0:
                print(f"DIPLOMATE | {n} lette, {dip} diplomate ({100*dip/n:.1f}%), "
                      f"{int(time.time()-t0)}s", flush=True)
    print(f"DIPLOMATE | lette {n}, diplomate {dip} ({100*dip/max(n,1):.1f}%), "
          f"di cui {senza} senza id del pool", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
