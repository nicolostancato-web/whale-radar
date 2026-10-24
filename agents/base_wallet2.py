"""L'IDENTITA' DEI COMPRATORI SUI POOL ATTIVI DI BASE, e se qualcuno vale copiarlo.

Si parte dai 40 pool piu' scambiati (li' c'e' sempre una controparte: nei pool nuovi di Base
l'82% delle posizioni resta bloccata, quindi copiare non avrebbe senso).

L'identita' NON e' il mittente dello Swap, che e' il router. Si prende dal trasferimento del
gettone: chi lo riceve dal gestore ha comprato. Su Base i trasferimenti si possono chiedere
solo con l'indirizzo del gettone, quindi si risale al gettone dal lancio del pool.

Il giudizio e' quello di sempre: seguire i SUOI acquisti con il nostro ritardo, entrare su una
stampa di acquisto, uscire su una di vendita, e confrontare con la TARATURA dello stesso pool.
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base_rpc as B

SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
INIT = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
TRASF = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
SALTO = 150          # 5 minuti su Base
RITARDO = 1


def _sg(x):
    v = int(x, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def gettone(idp, t):
    """il gettone del pool, dal suo lancio: si cerca a fette perche' il nodo e' corto"""
    b = t - B.profondita(t)
    while b <= t:
        f = min(b + 5000, t)
        for l in B.log_di_finestra(INIT, b, f, indirizzo=B.GESTORE_V4) or []:
            if l["topics"][1] == idp:
                c0, c1 = "0x" + l["topics"][2][-40:], "0x" + l["topics"][3][-40:]
                return c1 if int(c0, 16) == 0 else c0
        b = f + 1
    return None


def main():
    t = B.testa()
    da = t - B.profondita(t)
    attivi = json.load(open("data/multichain/base/pool_attivi.json"))["pool_attivi"]
    print(f"BASE WALLET | {len(attivi)} pool attivi, finestra {t-da:,} blocchi", flush=True)
    per_pool = {}
    for k, idp in enumerate(attivi[:12]):
        tok = gettone(idp, t)
        if not tok:
            continue
        sw = collections.defaultdict(list)
        serie = []
        b = da
        while b <= t:
            f = min(b + B.FINESTRA - 1, t)
            for l in B.log_di_finestra(SW, b, f, indirizzo=B.GESTORE_V4, secondo=idp) or []:
                d = l["data"][2:]
                if len(d) < 128:
                    continue
                a0, a1 = _sg(d[0:64]), _sg(d[64:128])
                if a0 and a1:
                    serie.append((int(l["blockNumber"], 16), abs(a0 / a1), a0 < 0))
                    sw[l["transactionHash"]].append(1)
            for l in B.log_di_finestra(TRASF, b, f, indirizzo=tok) or []:
                if len(l.get("topics", [])) < 3:
                    continue
                mitt, dest = "0x" + l["topics"][1][-40:], "0x" + l["topics"][2][-40:]
                if mitt != B.GESTORE_V4 or l["transactionHash"] not in sw:
                    continue
                per_pool.setdefault(idp, []).append((int(l["blockNumber"], 16), dest))
            b = f + 1
            time.sleep(0.1)
        per_pool.setdefault(idp, [])
        per_pool[idp] = (sorted(serie), sorted(per_pool[idp]))
        print(f"   {k+1}/12 pool {idp[:12]}: {len(serie):,} scambi, "
              f"{len(per_pool[idp][1]):,} acquisti con nome", flush=True)
    # giudizio: per ogni portafoglio, seguire i SUOI acquisti
    def segui(P, blocco):
        ing = next((j for j in range(len(P)) if P[j][0] >= blocco + RITARDO and P[j][2]), None)
        if ing is None or P[ing][1] <= 0:
            return None
        usc = next((k for k in range(ing + 1, len(P))
                    if P[k][0] >= P[ing][0] + SALTO and not P[k][2]), None)
        if usc is None:
            return ("bloccata", P[-1][1] / P[ing][1] - 1)
        return ("chiusa", P[usc][1] / P[ing][1] - 1)
    chi = collections.defaultdict(list)
    tara = []
    for idp, (P, acquisti) in per_pool.items():
        if len(P) < 50:
            continue
        for i, (b, p, compra) in enumerate(P):
            if compra:
                r = segui(P, b)
                if r:
                    tara.append(r[1] if r[0] == "chiusa" else -1.0)
        for b, w in acquisti:
            r = segui(P, b)
            if r:
                chi[w].append(r[1] if r[0] == "chiusa" else -1.0)
    print(f"\n   indirizzi compratori distinti: {len(chi):,}")
    if tara:
        print(f"   riferimento, seguendo QUALUNQUE acquisto: {statistics.median(tara)*100:+.2f}% "
              f"su {len(tara):,} operazioni")
    buoni = {w: v for w, v in chi.items() if len(v) >= 8}
    print(f"   portafogli con almeno 8 acquisti: {len(buoni):,}")
    if buoni:
        m = sorted(((statistics.median(v), len(v), w) for w, v in buoni.items()), reverse=True)
        print(f"   migliori: " + ", ".join(f"{w[:10]} {x*100:+.1f}% su {n}" for x, n, w in m[:5]))
        tutti = [statistics.median(v) for v in buoni.values()]
        print(f"   mediana su tutti i portafogli: {statistics.median(tutti)*100:+.2f}%")
    json.dump({w: v for w, v in list(chi.items())[:5000]},
              open("data/multichain/base/wallet_esiti.json", "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
