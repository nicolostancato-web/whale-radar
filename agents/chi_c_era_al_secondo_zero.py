"""CHI C'ERA AL SECONDO ZERO — scelti dal momento, mai dal profitto.

PERCHE' QUESTA CHIUDE IL DISCORSO (23/10). Finora i portafogli «al secondo zero» erano tre, ed
erano proprio quelli che avevo gia' identificato come vincenti: la tabella descriveva loro, non
il fenomeno. Il senno di poi non era sparito, si era nascosto.

Qui si parte dall'altro capo e il profitto non entra mai nella selezione: nei 131 gettoni di
cui abbiamo la VITA INTERA (verificato: nessuno tocca il tetto delle firme, quindi il primo
scambio e' la nascita), si prende chi compra nei primissimi istanti. Poi, SEPARATAMENTE, si
guarda come e' andata.

Chi non ha mai venduto vale -100% di quanto ha speso: non si scarta.
"""
import collections, json, os, statistics, sys

DENTRO = "data/multichain/solana/gettoni.jsonl"
FASCE = [("stesso istante", 0, 1), ("1-5 slot", 1, 5), ("5-25 slot", 5, 25),
         ("25-150 slot", 25, 150), ("oltre", 150, 10 ** 9)]


def main():
    agg = collections.defaultdict(lambda: {"res": [], "wal": set(), "mint": set(), "speso": 0.0})
    nm = 0
    for r in open(DENTRO):
        d = json.loads(r)
        P = sorted(d["s"])
        if len(P) < 20 or len(P[0]) < 5:
            continue
        nm += 1
        s0 = P[0][0]
        per = collections.defaultdict(lambda: {"c": 0.0, "v": 0.0, "slot": None})
        for riga in P:
            sl, p, compra, chi = riga[0], riga[1], riga[2], riga[3]
            sol = riga[4] if len(riga) > 4 else 0.0
            k = per[chi]
            if compra:
                k["c"] += sol
                k["slot"] = sl if k["slot"] is None else min(k["slot"], sl)
            else:
                k["v"] += sol
        for chi, k in per.items():
            if k["c"] <= 0 or k["slot"] is None:
                continue
            rit = k["slot"] - s0
            esito = k["v"] / k["c"] - 1
            for et, a, b in FASCE:
                if a <= rit < b:
                    g = agg[et]
                    g["res"].append(esito)
                    g["wal"].add(chi)
                    g["mint"].add(d["g"])
                    g["speso"] += k["c"]
                    break
    print(f"CHI C'ERA AL SECONDO ZERO | {nm} gettoni con la vita intera\n")
    print(f"   {'quando entra':<20}{'posizioni':>11}{'portafogli':>12}{'gettoni':>9}"
          f"{'resa mediana':>15}{'in utile':>10}{'SOL spesi':>12}")
    print('   ' + '-' * 90)
    for et, _, _ in FASCE:
        g = agg.get(et)
        if not g or len(g["res"]) < 5:
            print(f"   {et:<20}{len(g['res']) if g else 0:>11}   (poche)")
            continue
        r = g["res"]
        print(f"   {et:<20}{len(r):>11}{len(g['wal']):>12}{len(g['mint']):>9}"
              f"{statistics.median(r)*100:>+14.1f}%{sum(1 for x in r if x>0)/len(r)*100:>9.0f}%"
              f"{g['speso']:>12.2f}")
    print('   ' + '-' * 90)
    print("   nessun portafoglio e' entrato in questa tabella per aver guadagnato:")
    print("   la fascia dipende solo da QUANDO ha comprato.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
