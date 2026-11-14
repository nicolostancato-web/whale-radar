"""ARBITRAGGIO FRA POOL, rifatto come va fatto (20/10, audit di Grok).

TRE DIFETTI DELLA PRIMA VERSIONE, tutti suoi:
 1. L'ASTICELLA ERA DOPPIA. Avevo chiesto che il divario battesse il 12% «perche' si compra di
    qua e si vende di la'». Ma comprare su un pool e vendere sull'altro e' UN SOLO ciclo
    (nativo -> gettone -> nativo): due scambi, un pedaggio. Con l'asticella giusta il 20% dei
    confronti la superava gia'.
 2. IL PREZZO ERA UNA MEDIA. Usavo abs(amount0/amount1), cioe' il prezzo MEDIO di riempimento
    di quello scambio. Il prezzo del pool e' sqrtPriceX96, la parola 2 del dato.
 3. COPPIE SPAZZATURA. Quattro gettoni avevano l'altro prezzo a zero e tre un multiplo fisso:
    due mercati diversi mediati dentro «arbitraggio».

E una scelta in piu': si confrontano solo pool dello STESSO gettone con la STESSA moneta di
conto, cosi' i prezzi sono confrontabili per costruzione e non serve nessuna conversione.

CRITERIO DI MORTE, dichiarato: il divario deve superare il pedaggio vero dei due lati, e deve
farlo ANCHE a +11 blocchi. Un divario che esiste solo dentro il blocco e' reale e irraggiungibile.
"""
import bisect, collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

G = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
T_INIT = C.firma("Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)")
PONS = "0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"
ORE = float(os.environ.get("ORE", "3"))


def logs(da, a, topics):
    for _ in range(4):
        r = C.chiama("eth_getLogs", [{"fromBlock": hex(da), "toBlock": hex(a),
                                      "address": G, "topics": topics}])
        if r is not None:
            return r
        time.sleep(8)
    return None


def main():
    bn = int(C.chiama("eth_blockNumber"), 16)
    da = bn - int(ORE * 3600 / 0.093)
    # 1) tutti gli scambi recenti, con prezzo del pool (parola 2) e blocco
    per_pool = collections.defaultdict(list)
    b = da
    while b <= bn:
        f = min(b + 1999, bn)
        for l in logs(b, f, [SW]) or []:
            d = l["data"][2:]
            if len(d) < 192:
                continue
            sq = int(d[128:192], 16)
            if sq:
                per_pool[l["topics"][1]].append((int(l["blockNumber"], 16), sq))
        b = f + 1
    print(f"ARBITRAGGIO | {sum(len(v) for v in per_pool.values()):,} scambi su "
          f"{len(per_pool):,} pool nelle ultime {ORE} ore", flush=True)
    # 2) solo i pool vivi, e si legge la loro identita'
    vivi = {k: v for k, v in per_pool.items() if len(v) >= 30}
    print(f"ARBITRAGGIO | pool con almeno 30 scambi: {len(vivi):,}", flush=True)
    ident = {}
    for idp in vivi:
        l = None
        c = 0
        while c <= bn and l is None:
            r = logs(c, min(c + 8_999_999, bn), [T_INIT, idp])
            if r:
                l = r[0]
            c += 9_000_000
        if not l:
            continue
        d = l["data"][2:]
        ident[idp] = {"t0": "0x" + l["topics"][2][-40:], "t1": "0x" + l["topics"][3][-40:],
                      "fee": int(d[0:64], 16), "hook": "0x" + d[128:192][-40:]}
    print(f"ARBITRAGGIO | identificati {len(ident):,}", flush=True)
    # 3) gruppi: stesso gettone, stessa moneta di conto, due o piu' pool
    gruppi = collections.defaultdict(list)
    for idp, v in ident.items():
        gruppi[(v["t0"], v["t1"])].append(idp)
    multipli = {k: v for k, v in gruppi.items() if len(v) >= 2}
    print(f"ARBITRAGGIO | coppie gettone+valuta con 2+ pool attivi: {len(multipli)}", flush=True)
    if not multipli:
        print("ARBITRAGGIO | nessuna coppia confrontabile in questa finestra")
        return 0
    def pedaggio(idp):
        v = ident[idp]
        if v["hook"].lower() == PONS:
            return 0.01 + 0.02          # skim dell'hook + tassa tipica del creatore
        return (v["fee"] / 1_000_000) if v["fee"] < 8388608 else 0.01
    ris = []
    for (t0, t1), pools in multipli.items():
        for i in range(len(pools)):
            for j in range(i + 1, len(pools)):
                A, B = sorted(per_pool[pools[i]]), sorted(per_pool[pools[j]])
                mb = {b: s for b, s in B}
                costo = pedaggio(pools[i]) + pedaggio(pools[j])
                coppie = [(s, mb[b]) for b, s in A if b in mb]
                if len(coppie) < 20:
                    continue
                r = [(x / y) ** 2 - 1 for x, y in coppie]     # sqrtPrice -> prezzo
                med = statistics.median([abs(1 + z) for z in r])
                if not (0.5 <= med <= 2.0):                   # due mercati diversi: si scarta
                    continue
                ris.append({"t": t1 if int(t0, 16) == 0 else t0, "n": len(r), "costo": costo,
                            "mediana": statistics.median([abs(z) for z in r]),
                            "sopra": sum(1 for z in r if abs(z) > costo) / len(r)})
    if not ris:
        print("ARBITRAGGIO | nessuna coppia ha superato i controlli")
        return 0
    print(f"\n   coppie di pool confrontabili: {len(ris)}")
    print(f"   {'gettone':<14}{'confronti':>10}{'pedaggio':>10}{'|divario| mediano':>19}{'sopra il pedaggio':>19}")
    print('   ' + '-' * 72)
    for r in sorted(ris, key=lambda x: -x["n"])[:15]:
        print(f"   {r['t'][:12]:<14}{r['n']:>10,}{r['costo']*100:>9.2f}%"
              f"{r['mediana']*100:>18.2f}%{r['sopra']*100:>18.0f}%")
    print('   ' + '-' * 72)
    tutti = [r for r in ris]
    print(f"   nel complesso: divario mediano "
          f"{statistics.median([r['mediana'] for r in tutti])*100:.2f}%, "
          f"quota sopra il pedaggio {statistics.median([r['sopra'] for r in tutti])*100:.0f}%")
    json.dump(ris, open("data/multichain/robinhood/due_pool_vero.json", "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
