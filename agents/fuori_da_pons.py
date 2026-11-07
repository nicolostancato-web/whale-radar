"""L'ALTRO 87% DELLA CHAIN: la prova del ritardo sui pool che NON sono di Pons.

PERCHE' (20/10, obiezione del fondatore e audit di Grok). Abbiamo dichiarato chiusa «la chain»
avendo misurato solo i 10.332 diplomati di Pons. Ma nell'ultima ora 13 dei 15 pool piu' attivi
NON sono di Pons, e molti hanno una commissione vera per chi mette liquidita' (0,30%, 0,05%)
invece dello zero dei pool di Pons. Sono un mercato diverso, mai misurato.

Qui si rifa' esattamente la prova che ha chiuso Pons — comprare dopo un acquisto, entrare a
+11 blocchi (il nostro secondo misurato), uscire su una stampa di VENDITA — ma su quel mercato.
Se anche li' la resa e' negativa, la chain e' chiusa per davvero. Se no, abbiamo sbagliato
universo e non strategia.
"""
# IL SEGNO, VERIFICATO SULLA CHAIN (21/10). a0 POSITIVO vuol dire che l'utente ha
# VENDUTO, non comprato: incrociando gli Swap con i trasferimenti del gettone, quando il
# gestore MANDA gettoni (cioe' l'utente compra) a0 e' NEGATIVO. Con il segno invertito si
# misura il mestiere di chi incassa lo spread invece di chi lo paga, e la resa viene pari
# al DOPPIO della commissione del pool: 1,00%% -> +1,96%%, 0,30%% -> +0,49%%, zero -> -0,06%%.
# Quella proporzionalita' esatta e' stata la spia che ha fatto scoprire l'errore.
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

G = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
T_INIT = C.firma("Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)")
PONS = "0xe5e702641ea86f4ae6cc3cdaed2b886f976be044"
ORE = float(os.environ.get("ORE", "12"))
# SPOSTA indietro la finestra: serve una seconda finestra NON sovrapposta per la prova
# fuori campione. Un risultato che vale su un periodo solo non e' ancora un risultato.
INDIETRO = float(os.environ.get("INDIETRO", "0"))
FUORI = os.environ.get("FUORI", "data/multichain/robinhood/fuori_da_pons.json")


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
    bn = bn - int(INDIETRO * 3600 / 0.093)
    da = bn - int(ORE * 3600 / 0.093)
    per = collections.defaultdict(list)
    b = da
    n = 0
    while b <= bn:
        f = min(b + 1999, bn)
        for l in logs(b, f, [SW]) or []:
            d = l["data"][2:]
            if len(d) < 128:
                continue
            def sg(x):
                v = int(x, 16)
                return v - (1 << 256) if v >= (1 << 255) else v
            a0, a1 = sg(d[0:64]), sg(d[64:128])
            if a0 and a1:
                per[l["topics"][1]].append((int(l["blockNumber"], 16), abs(a0 / a1), a0 < 0))
        b = f + 1
        n += 1
        if n % 200 == 0:
            print(f"   {b-da:,}/{bn-da:,} blocchi, {len(per):,} pool", flush=True)
    vivi = {k: sorted(v) for k, v in per.items() if len(v) >= 60}
    print(f"FUORI DA PONS | {len(vivi):,} pool con almeno 60 scambi in {ORE} ore", flush=True)
    # TUTTI I LANCI IN UNA PASSATA SOLA (20/10). Cercare il lancio di ogni pool lungo tutta la
    # chain costa fino a 11 chiamate per pool: su 1.291 pool sono 14.000 chiamate e la notte
    # non basta. Gli Initialize si leggono tutti in 11 chiamate e si mettono in una mappa.
    # 21/10: leggere TUTTI gli Initialize della chain non si puo' — sono oltre un milione e
    # l'RPC rifiuta la finestra. Ma l'elenco dei pool di Pons ce l'abbiamo gia': e' il
    # manifesto costruito il 19/10 leggendo la fabbrica. Chi non e' li' dentro non e' di Pons.
    man = json.load(open("data/multichain/robinhood/manifesto_graduati.json"))["pool"]
    insieme_pons = set(man)
    pons = [i for i in vivi if i in insieme_pons]
    altri = [i for i in vivi if i not in insieme_pons]
    print(f"FUORI DA PONS | di Pons {len(pons):,}, altri {len(altri):,}", flush=True)

    def resa(P):
        """comprare dopo un acquisto, entrare a +11 blocchi, uscire sulla prima VENDITA."""
        out = []
        for i, (b_, p, compra) in enumerate(P):
            if not compra:
                continue
            j0 = None
            for j in range(i + 1, len(P)):
                if P[j][0] >= b_ + 11:
                    j0 = j
                    break
            if j0 is None or P[j0][1] <= 0:
                continue
            p0 = P[j0][1]
            for j in range(j0 + 1, len(P)):
                if not P[j][2]:
                    out.append(P[j][1] / p0 - 1)
                    break
        return out

    ris = {}
    for et, elenco in (("Pons", pons), ("non-Pons", altri)):
        per_pool = []
        for idp in elenco:
            v = resa(vivi[idp])
            if len(v) >= 10:
                per_pool.append(statistics.mean(v))
        if len(per_pool) < 5:
            print(f"   {et}: troppi pochi pool")
            continue
        ris[et] = per_pool
        print(f"   {et:<10}{len(per_pool):>5} pool   resa media {statistics.mean(per_pool)*100:>+7.2f}% "
              f"+/-{1.96*statistics.stdev(per_pool)/len(per_pool)**0.5*100:.2f}   "
              f"mediana {statistics.median(per_pool)*100:>+7.2f}%   "
              f"pool in utile {sum(1 for x in per_pool if x>0)/len(per_pool)*100:.0f}%")
    json.dump({k: v for k, v in ris.items()}, open(FUORI, "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
