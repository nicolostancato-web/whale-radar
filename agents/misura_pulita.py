"""LA MISURA PULITA: con il metro tarato, cosa rende seguire un acquisto su questa chain.

Tre regole imparate a caro prezzo nella notte del 20-21/10, tutte dentro questo file:
 1. IL SEGNO: a0 NEGATIVO = l'utente compra (verificato sulla chain incrociando gli Swap con i
    trasferimenti). Con il verso sbagliato la resa viene pari al doppio della commissione.
 2. I DUE LATI DEL LIBRO: si ENTRA al prezzo di una stampa di ACQUISTO (quello che paghiamo) e
    si ESCE al prezzo di una stampa di VENDITA (quello che incassiamo). Mai una stampa qualunque.
 3. LA RIGA DI TARATURA resta nella tabella per sempre: il giro istantaneo DEVE essere negativo
    e proporzionale alla commissione. Se quella riga non torna, la tabella non si legge.
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

G = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
ORE = float(os.environ.get("ORE", "6"))
ORIZZONTI = [("taratura (subito)", 0), ("+1 minuto", 645), ("+5 minuti", 3225), ("+30 minuti", 19354)]


def main():
    bn = int(C.chiama("eth_blockNumber"), 16)
    da = bn - int(ORE * 3600 / 0.093)
    per = collections.defaultdict(list)
    fee = {}
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
            per[l["topics"][1]].append((int(l["blockNumber"], 16), abs(a0 / a1), a0 < 0))
            fee[l["topics"][1]] = int(d[320:384], 16)
        b = f + 1
    man = set(json.load(open("data/multichain/robinhood/manifesto_graduati.json"))["pool"])
    vivi = {k: sorted(v) for k, v in per.items() if len(v) >= 80}
    print(f"PULITA | {len(vivi):,} pool con almeno 80 scambi in {ORE} ore\n", flush=True)

    def rese(P):
        """Tutti gli orizzonti insieme, e SOLO le operazioni che esistono a tutti.

        4. (21/10) OGNI ORIZZONTE DEVE AVERE GLI STESSI CASI. Misurando ogni colonna sul suo
        insieme, a 5 minuti veniva +101% e a 30 minuti -0,68%: non due orizzonti, due
        popolazioni. Chi non ha una vendita a 30 minuti e' escluso da TUTTE le colonne.
        """
        out = {e: [] for e, _ in ORIZZONTI}
        for i, (b_, p, compra) in enumerate(P):
            if not compra:
                continue
            ing = next((j for j in range(i + 1, len(P))
                        if P[j][0] >= b_ + 11 and P[j][2]), None)
            if ing is None or P[ing][1] <= 0:
                continue
            usc = {}
            for e, salto in ORIZZONTI:
                j = next((k for k in range(ing + 1, len(P))
                          if P[k][0] >= P[ing][0] + salto and not P[k][2]), None)
                if j is None:
                    break
                usc[e] = P[j][1] / P[ing][1] - 1
            if len(usc) == len(ORIZZONTI):
                for e in usc:
                    out[e].append(usc[e])
        return out

    gruppi = collections.defaultdict(list)
    for idp, P in vivi.items():
        f = fee.get(idp, 0)
        et = "PONS" if idp in man else ("dinamica" if f >= 8388608 else
                                        ("senza commissione" if f == 0 else f"commissione {f/10000:.2f}%"))
        gruppi[et].append(P)
    print(f"   {'gruppo':<22}{'pool':>6}" + "".join(f"{e:>19}" for e, _ in ORIZZONTI))
    print('   ' + '-' * 104)
    for et, elenco in sorted(gruppi.items(), key=lambda kv: -len(kv[1]))[:7]:
        tutte = [rese(P) for P in elenco]
        tutte = [d for d in tutte if len(d[ORIZZONTI[0][0]]) >= 10]
        riga = f"   {et:<22}{len(tutte):>6}"
        for e, _ in ORIZZONTI:
            m = [statistics.median(d[e]) for d in tutte]
            riga += (f"{statistics.median(m)*100:>+17.2f}% " if len(m) >= 8 else f"{'pochi':>19}")
        print(riga, flush=True)
    print('   ' + '-' * 104)
    print("   la prima colonna e' la TARATURA: deve essere negativa e crescere col costo del pool.")
    print("   se non lo e', il resto della riga non si legge.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
