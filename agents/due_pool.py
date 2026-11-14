"""ARBITRAGGIO FRA DUE POOL dello stesso gettone: l'ultima posizione senza previsione.

Il 24% dei gettoni diplomati vive in piu' di un pool, e 21 secondi pool su 25 scambiano
davvero. Se i due prezzi divergono in modo sistematico, chi compra nel pool basso e vende in
quello alto incassa la differenza senza prevedere nulla.

DUE CONTROLLI PRIMA DI CREDERCI, scritti ora:
 1. ENTRAMBI i pool devono essere quotati in NATIVO. Confrontare un prezzo in nativo con uno
    in un altro gettone e' l'artefatto che ha gia' gonfiato un numero di questo progetto di
    cinque ordini di grandezza.
 2. Lo scarto si misura solo quando i due prezzi sono VICINI NEL TEMPO (entro 600 blocchi,
    circa un minuto): due prezzi lontani divergono perche' il mercato si e' mosso, non perche'
    c'e' un arbitraggio.

CRITERIO DI MORTE: lo scarto mediano in valore assoluto deve superare il costo di DUE giri
(~12%, perche' si compra di qua e si vende di la') su entrambe le meta' del periodo.
"""
import bisect, collections, json, os, random, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

G = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
QUANTI = int(os.environ.get("QUANTI", "150"))
VICINO = 600


def _segno(v):
    return v - (1 << 256) if v >= (1 << 255) else v


def serie(idp, da):
    lg = C.log_di_finestra(SW, da, da + 400_000, indirizzo=G, secondo=idp)
    if not lg:
        return []
    out = []
    for l in lg:
        d = l["data"][2:]
        if len(d) < 128:
            continue
        a0, a1 = _segno(int(d[0:64], 16)) / 1e18, _segno(int(d[64:128], 16)) / 1e18
        if a0 and a1:
            out.append((int(l["blockNumber"], 16), abs(a0 / a1)))
    out.sort()
    return out


def main():
    man = json.load(open("data/multichain/robinhood/manifesto_graduati.json"))["pool"]
    cp = json.load(open("data/multichain/robinhood/coppie.json"))["coppie"]
    pons = {v["moneta"].lower(): (k, v["diploma"]) for k, v in man.items()
            if int(v["valuta"], 16) == 0}
    per_tok = collections.defaultdict(list)
    for k, v in cp.items():
        for t in (v["t0"], v["t1"]):
            t = t.lower()
            if t in pons:
                per_tok[t].append((k, v))
    cand = []
    for t, l in per_tok.items():
        if not (2 <= len(l) <= 4):
            continue
        altri = [(k, v) for k, v in l if k != pons[t][0]
                 and (int(v["t0"], 16) == 0 or int(v["t1"], 16) == 0)]   # anche l'altro in NATIVO
        if altri:
            cand.append((t, altri[0][0]))
    print(f"DUE POOL | gettoni con due pool entrambi in nativo: {len(cand):,}", flush=True)
    camp = random.Random(55).sample(cand, min(QUANTI, len(cand)))
    righe = []
    for i, (t, idp_b) in enumerate(camp):
        idp_a, dip = pons[t]
        A, B = serie(idp_a, dip), serie(idp_b, dip)
        if len(A) < 5 or len(B) < 5:
            continue
        bl = [x[0] for x in A]
        for b, pb in B:
            j = bisect.bisect_right(bl, b) - 1
            if j < 0 or b - bl[j] > VICINO:
                continue
            pa = A[j][1]
            if pa > 0:
                righe.append({"moneta": t, "diploma": dip, "scarto": pb / pa - 1})
        if (i + 1) % 25 == 0:
            print(f"   {i+1}/{len(camp)} ... confronti finora {len(righe):,}", flush=True)
        time.sleep(0.2)
    if len(righe) < 100:
        print(f"DUE POOL | solo {len(righe)} confronti: troppo pochi")
        return 0
    json.dump(righe, open("data/multichain/robinhood/due_pool.json", "w"))
    righe.sort(key=lambda x: x["diploma"])
    mz = len(righe) // 2
    print(f"\n   confronti: {len(righe):,} su {len({r['moneta'] for r in righe})} gettoni")
    print(f"   {'periodo':<16}{'confronti':>11}{'|scarto| mediano':>18}{'sopra 12%':>12}")
    print('   ' + '-' * 58)
    for et, fetta in (("prima meta", righe[:mz]), ("seconda meta", righe[mz:]), ("tutte", righe)):
        v = [abs(r["scarto"]) for r in fetta]
        print(f"   {et:<16}{len(v):>11,}{statistics.median(v)*100:>17.2f}%"
              f"{sum(1 for x in v if x > 0.12)/len(v)*100:>11.0f}%")
    print('   ' + '-' * 58)
    return 0


if __name__ == "__main__":
    sys.exit(main())
