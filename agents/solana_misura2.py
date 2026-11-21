"""LA MISURA SU SOLANA, sull'archivio per gettone. Taratura in cima, sempre.

Le quattro lezioni delle due notti precedenti sono tutte dentro:
 1. il verso viene dalla tasca di chi firma (e la taratura lo riverifica)
 2. si entra su una stampa di ACQUISTO e si esce su una di VENDITA
 3. la taratura e' la prima colonna: se non e' negativa, la riga non si legge
 4. stessi casi in tutte le colonne, e le posizioni senza uscita CONTATE, non scartate
"""
import json, os, statistics, sys

DENTRO = "data/multichain/solana/gettoni.jsonl"
RITARDO = 3                      # ~1 secondo: uno slot dura ~0,4s
ORIZZONTI = [("taratura (subito)", 0), ("+1 minuto", 150), ("+5 minuti", 750)]


def rese(P):
    out = {e: [] for e, _ in ORIZZONTI}
    bloc = tot = 0
    for i, (sl, p, compra, chi) in enumerate(P):
        if not compra:
            continue
        ing = next((j for j in range(i + 1, len(P)) if P[j][0] >= sl + RITARDO and P[j][2]), None)
        if ing is None or P[ing][1] <= 0:
            continue
        tot += 1
        u = {}
        for e, salto in ORIZZONTI:
            j = next((k for k in range(ing + 1, len(P))
                      if P[k][0] >= P[ing][0] + salto and not P[k][2]), None)
            if j is None:
                break
            u[e] = P[j][1] / P[ing][1] - 1
        if len(u) == len(ORIZZONTI):
            for e in u:
                out[e].append(u[e])
        else:
            bloc += 1
    return out, bloc, tot


def main():
    if not os.path.exists(DENTRO):
        print("MISURA SOL | niente archivio")
        return 0
    print(f"   {'gettone':<16}{'scambi':>8}" + "".join(f"{e:>19}" for e, _ in ORIZZONTI) + f"{'bloccate':>11}")
    print('   ' + '-' * 92)
    agg = {e: [] for e, _ in ORIZZONTI}
    n = 0
    for r in open(DENTRO):
        d = json.loads(r)
        P = sorted(d["s"])
        o, bloc, tot = rese(P)
        if len(o[ORIZZONTI[0][0]]) < 5:
            continue
        n += 1
        riga = f"   {d['g'][:14]:<16}{d['n']:>8}"
        for e, _ in ORIZZONTI:
            m = statistics.median(o[e])
            agg[e].append(m)
            riga += f"{m*100:>+17.2f}% "
        riga += f"{bloc/max(1,tot)*100:>9.0f}%"
        print(riga)
    print('   ' + '-' * 92)
    if n >= 3:
        print("   " + "mediana fra i gettoni:".ljust(24)
              + "".join(f"{statistics.median(agg[e])*100:>+17.2f}% " for e, _ in ORIZZONTI))
    print(f"\n   gettoni misurati: {n}. La prima colonna deve essere NEGATIVA.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
