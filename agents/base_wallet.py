"""CHI COMPRA COSA SU BASE, e se vale copiarlo.

Due vincoli di Base, entrambi MISURATI oggi e non assunti:
 - l'RPC rifiuta le query sui trasferimenti senza indirizzo («Please specify an address»),
   quindi l'identita' si prende gettone per gettone, non in blocco
 - il nodo serve solo le ultime ~5 ore, quindi si lavora su una finestra corta e si accumula

Si parte dai pool PIU' ATTIVI: e' li' che un portafoglio copiabile opererebbe, ed e' li' che
c'e' sempre qualcuno a cui vendere — che su Base, nei pool nuovi, manca nell'82% dei casi.

Il metro e' quello di sempre: entrata su un acquisto, uscita su una vendita, taratura in cima,
posizioni bloccate contate e non scartate.
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_rpc as B

SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
TRASF = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
QUANTI = int(os.environ.get("QUANTI", "40"))
FUORI = "data/multichain/base/wallet.jsonl"


def _sg(x):
    v = int(x, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def main():
    t = B.testa()
    prof = B.profondita(t)
    da = t - prof
    print(f"BASE WALLET | finestra {prof:,} blocchi ({prof*B.BLOCCO/3600:.1f} ore)", flush=True)
    swap = collections.defaultdict(list)
    tx_pool = collections.defaultdict(list)
    b = da
    while b <= t:
        f = min(b + B.FINESTRA - 1, t)
        for l in B.log_di_finestra(SW, b, f, indirizzo=B.GESTORE_V4) or []:
            d = l["data"][2:]
            if len(d) < 384:
                continue
            a0, a1 = _sg(d[0:64]), _sg(d[64:128])
            if not (a0 and a1):
                continue
            idp = l["topics"][1]
            swap[idp].append((int(l["blockNumber"], 16), abs(a0 / a1), a0 < 0))
            tx_pool[l["transactionHash"]].append((idp, a0, a1))
        b = f + 1
        time.sleep(0.15)
    attivi = sorted(swap, key=lambda k: -len(swap[k]))[:QUANTI]
    print(f"BASE WALLET | {len(swap):,} pool, prendo i {len(attivi)} piu' attivi "
          f"({len(swap[attivi[0]]):,} scambi il primo)", flush=True)
    # per ogni pool attivo serve il GETTONE: lo si trova dal trasferimento nella stessa tx
    # Qui si fa il contrario ed e' piu' economico: si leggono i trasferimenti dei gettoni che
    # compaiono nelle transazioni di quei pool.
    print("   (identita' dei compratori: in costruzione nel prossimo giro)", flush=True)
    os.makedirs("data/multichain/base", exist_ok=True)
    json.dump({"pool_attivi": attivi, "scambi": {k: len(swap[k]) for k in attivi}},
              open("data/multichain/base/pool_attivi.json", "w"))
    print(f"BASE WALLET | elenco dei pool attivi salvato: {len(attivi)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
