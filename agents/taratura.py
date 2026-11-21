"""IL CASO DI TARATURA: una misura di cui conosciamo gia' la risposta.

PERCHE' (21/10). Stanotte il segno degli scambi mi ha ingannato due volte, in direzioni
opposte, e ragionarci sopra non basta piu': serve un caso in cui la risposta e' nota PRIMA di
misurare, cosi' lo strumento si tara invece di essere argomentato.

IL CASO: comprare e rivendere SUBITO, senza tenere nulla. Si entra al prezzo di una stampa di
ACQUISTO (quello che paga chi compra) e si esce alla prima stampa di VENDITA successiva (quello
che incassa chi vende). Non c'e' tempo perche' il mercato si muova: il risultato DEVE essere
negativo, e grande piu' o meno quanto il giro completo di quel pool.

Se viene positivo, la catena ha ancora il verso sbagliato e nessun altro numero vale.
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import curva_pons as C

G = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
SW = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
ORE = float(os.environ.get("ORE", "3"))


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
            # verificato sulla chain il 21/10: a0 NEGATIVO = l'utente COMPRA
            per[l["topics"][1]].append((int(l["blockNumber"], 16), abs(a0 / a1), a0 < 0))
            fee[l["topics"][1]] = int(d[320:384], 16)
        b = f + 1
    man = set(json.load(open("data/multichain/robinhood/manifesto_graduati.json"))["pool"])
    vivi = {k: sorted(v) for k, v in per.items() if len(v) >= 60}
    print(f"TARATURA | {len(vivi):,} pool con almeno 60 scambi in {ORE} ore\n")

    def giro_istantaneo(P):
        """compro al prezzo di un ACQUISTO, rivendo alla prima VENDITA subito dopo."""
        out = []
        for i, (b_, p, compra) in enumerate(P):
            if not compra:
                continue
            for j in range(i + 1, min(i + 12, len(P))):
                if not P[j][2] and p > 0:
                    out.append(P[j][1] / p - 1)
                    break
        return out

    g = collections.defaultdict(list)
    for idp, P in vivi.items():
        v = giro_istantaneo(P)
        if len(v) < 10:
            continue
        f = fee.get(idp, 0)
        et = "dinamica" if f >= 8388608 else ("Pons (fee 0, hook)" if idp in man else
                                              ("zero" if f == 0 else f"{f/10000:.2f}%"))
        g[et].append(statistics.median(v))
    print(f"   {'pool':<22}{'quanti':>8}{'giro istantaneo':>18}{'atteso':>12}")
    print('   ' + '-' * 62)
    for et, l in sorted(g.items(), key=lambda kv: -len(kv[1]))[:8]:
        att = "negativo"
        print(f"   {et:<22}{len(l):>8}{statistics.median(l)*100:>+17.2f}%{att:>12}")
    print('   ' + '-' * 62)
    print("   se una sola riga e' POSITIVA, lo strumento e' ancora invertito.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
