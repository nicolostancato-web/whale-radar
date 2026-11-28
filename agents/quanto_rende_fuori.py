"""IL SEGNO ERA INVERTITO (21/10): a0 POSITIVO = l'utente ha VENDUTO. Verificato sulla
chain incrociando gli Swap coi trasferimenti. La spia e' stata la resa pari al doppio della
commissione del pool su ogni fascia.

Il mezzo punto fuori da Pons: quanto costa davvero, e quante occasioni ci sono.

La resa mediana per pool e' +0,46% e +0,59% su due finestre non sovrapposte, con il 70-76% dei
pool in utile. Prima di chiamarlo un vantaggio servono tre cose che non abbiamo ancora:
 1. IL COSTO VERO di quei pool. La commissione sta nella parola 5 del dato dello Swap: si legge
    gratis da ogni scambio, senza cercare il lancio di ogni pool.
 2. QUANTE OCCASIONI al giorno, perche' mezzo punto su poche operazioni non e' un mestiere.
 3. SE REGGE AI POOL PICCOLI: un risultato che vive solo dove ci sono 60 scambi in 12 ore non
    e' trattabile.
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

G = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
ORE = float(os.environ.get("ORE", "12"))


def main():
    bn = int(C.chiama("eth_blockNumber"), 16)
    da = bn - int(ORE * 3600 / 0.093)
    per = collections.defaultdict(list)
    fee_di = {}
    b = da
    while b <= bn:
        f = min(b + 1999, bn)
        r = None
        for _ in range(4):
            r = C.chiama("eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(f),
                                          "address": G, "topics": [SW]}])
            if r is not None:
                break
            time.sleep(8)
        for l in r or []:
            d = l["data"][2:]
            if len(d) < 384:
                continue
            def sg(x):
                v = int(x, 16)
                return v - (1 << 256) if v >= (1 << 255) else v
            a0, a1 = sg(d[0:64]), sg(d[64:128])
            if not (a0 and a1):
                continue
            per[l["topics"][1]].append((int(l["blockNumber"], 16), abs(a0 / a1), a0 < 0, abs(a0)))
            fee_di[l["topics"][1]] = int(d[320:384], 16)      # parola 5 = commissione applicata
        b = f + 1
    man = set(json.load(open("data/multichain/robinhood/manifesto_graduati.json"))["pool"])
    vivi = {k: sorted(v) for k, v in per.items() if len(v) >= 60 and k not in man}
    print(f"RENDE | {len(vivi):,} pool non-Pons con almeno 60 scambi in {ORE} ore\n", flush=True)

    def operazioni(P):
        out = []
        for i, (b_, p, compra, size) in enumerate(P):
            if not compra:
                continue
            j0 = next((j for j in range(i + 1, len(P)) if P[j][0] >= b_ + 11), None)
            if j0 is None or P[j0][1] <= 0:
                continue
            p0 = P[j0][1]
            for j in range(j0 + 1, len(P)):
                if not P[j][2]:
                    out.append(P[j][1] / p0 - 1)
                    break
        return out

    righe = []
    for idp, P in vivi.items():
        v = operazioni(P)
        if len(v) >= 10:
            righe.append({"pool": idp, "n": len(v), "med": statistics.median(v),
                          "fee": fee_di.get(idp, 0), "scambi": len(P)})
    print(f"   pool valutabili: {len(righe):,}")
    print(f"   operazioni in {ORE} ore: {sum(r['n'] for r in righe):,}")
    print(f"\n   {'commissione':<14}{'pool':>7}{'operazioni':>12}{'resa mediana':>15}{'pool in utile':>15}")
    print('   ' + '-' * 64)
    g = collections.defaultdict(list)
    for r in righe:
        f = r["fee"]
        et = "dinamica" if f >= 8388608 else ("zero" if f == 0 else f"{f/10000:.2f}%")
        g[et].append(r)
    for et, l in sorted(g.items(), key=lambda kv: -len(kv[1]))[:8]:
        m = [x["med"] for x in l]
        costo = 0 if et in ("zero", "dinamica") else float(et[:-1]) / 100 * 2
        print(f"   {et:<14}{len(l):>7}{sum(x['n'] for x in l):>12,}{statistics.median(m)*100:>+14.2f}%"
              f"{sum(1 for x in m if x>0)/len(m)*100:>14.0f}%"
              + (f"   (costo giro {costo:.2f}%)" if costo else ""))
    print('   ' + '-' * 64)
    print(f"\n   {'scambi nel pool':<18}{'pool':>7}{'resa mediana':>15}{'pool in utile':>15}")
    for a, b_ in ((60, 150), (150, 400), (400, 1500), (1500, 10 ** 9)):
        l = [r for r in righe if a <= r["scambi"] < b_]
        if len(l) < 10:
            continue
        m = [x["med"] for x in l]
        print(f"   {f'{a}-{b_ if b_<10**9 else 9999}':<18}{len(l):>7}{statistics.median(m)*100:>+14.2f}%"
              f"{sum(1 for x in m if x>0)/len(m)*100:>14.0f}%")
    json.dump(righe, open("data/multichain/robinhood/quanto_rende_fuori.json", "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
