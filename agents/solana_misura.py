"""LA MISURA CALIBRATA SU SOLANA: seguire un acquisto paga, al netto del pedaggio?

Terza chain, stesso metro. Le quattro lezioni pagate su Robinhood e Base sono tutte qui:
 1. IL VERSO: su Solana si legge dalla tasca di chi firma — SOL in calo e gettone in salita
    = ha comprato. La TARATURA lo riverifica da sola a ogni giro.
 2. I DUE LATI DEL LIBRO: si entra su una stampa di ACQUISTO e si esce su una di VENDITA.
 3. LA RIGA DI TARATURA in cima: il giro istantaneo deve perdere. Misurata ieri: -3,85%.
 4. STESSI CASI IN TUTTE LE COLONNE, e le posizioni senza uscita contate, non scartate.

Il nostro ritardo: uno slot Solana dura ~0,4s, quindi un secondo sono ~3 slot. Si usa 3.
"""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solana_rpc as S

POOL = "58oQChx4yWmvKdwLLZzBi4ChoCc2fqCUWBkwMihLYQo2"
GETTONI = int(os.environ.get("GETTONI", "10"))
PER_GETTONE = int(os.environ.get("PER_GETTONE", "200"))
RITARDO = 3
ORIZZONTI = [("taratura (subito)", 0), ("+1 minuto", 150), ("+5 minuti", 750)]


def serie_di(g, costo):
    sig = S.rpc("getSignaturesForAddress", [g, {"limit": PER_GETTONE}]) or []
    out = []
    for x in sig:
        if x.get("err"):
            continue
        e = S.scambio(x["signature"])
        costo[0] += 1
        if e and e[4] == g:
            out.append((e[0], e[1], e[2]))
        time.sleep(0.02)
    out.sort()
    return out


def main():
    if not S.url():
        print("MISURA SOL | nessuna chiave valida")
        return 1
    costo = [0]
    r = S.rpc("getSignaturesForAddress", [POOL, {"limit": 120}]) or []
    conta = collections.Counter()
    for x in r:
        if x.get("err"):
            continue
        e = S.scambio(x["signature"])
        costo[0] += 1
        if e:
            conta[e[4]] += 1
    gettoni = [g for g, _ in conta.most_common(GETTONI)]
    print(f"MISURA SOL | {len(conta)} gettoni visti, ne seguo {len(gettoni)}", flush=True)
    righe = []
    for g in gettoni:
        s = serie_di(g, costo)
        print(f"   {g[:12]}: {len(s)} scambi", flush=True)
        if len(s) >= 30:
            righe.append((g, s))
    print(f"MISURA SOL | costo finora ~{costo[0]:,} crediti\n", flush=True)
    if not righe:
        print("   nessun gettone con abbastanza scambi")
        return 0

    def rese(P):
        out = {e: [] for e, _ in ORIZZONTI}
        bloc = 0
        tot = 0
        for i, (sl, p, compra) in enumerate(P):
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

    print(f"   {'gettone':<16}{'scambi':>8}" + "".join(f"{e:>19}" for e, _ in ORIZZONTI) + f"{'bloccate':>11}")
    print('   ' + '-' * 90)
    agg = {e: [] for e, _ in ORIZZONTI}
    for g, P in righe:
        d, bloc, tot = rese(P)
        if len(d[ORIZZONTI[0][0]]) < 5:
            continue
        riga = f"   {g[:14]:<16}{len(P):>8}"
        for e, _ in ORIZZONTI:
            m = statistics.median(d[e])
            agg[e].append(m)
            riga += f"{m*100:>+17.2f}% "
        riga += f"{bloc/max(1,tot)*100:>9.0f}%"
        print(riga, flush=True)
    print('   ' + '-' * 90)
    if agg[ORIZZONTI[0][0]]:
        print("   " + "mediana fra i gettoni:".ljust(24)
              + "".join(f"{statistics.median(agg[e])*100:>+17.2f}% " for e, _ in ORIZZONTI))
    print(f"\n   costo totale: ~{costo[0]:,} crediti Helius")
    return 0


if __name__ == "__main__":
    sys.exit(main())
