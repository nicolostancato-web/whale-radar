"""LA RELAZIONE CHE SPIEGA TRE MESI: il guadagno apparente vive dove non si puo' uscire.

Tre chain, sei falsi positivi, e ogni volta il numero bello stava dove una fetta grossa delle
posizioni non trovava nessuno a cui vendere. Su Base nei pool nuovi l'82%, su Solana dal 22%
al 56% a seconda del gettone, e sempre col guadagno apparente che cresce insieme.

Ha una spiegazione quasi ovvia una volta vista: un gettone il cui prezzo «sale» mentre nessuno
vende e' un gettone SENZA COMPRATORI VERI. Manca il lato che lo tirerebbe giu'.

Qui la relazione si misura direttamente, invece di dedurla. Se regge, il test da applicare a
qualunque mercato d'ora in poi non e' «quanto rende» ma «quanto rende, e quante delle posizioni
che lo producono si potevano chiudere davvero».
"""
import json, os, statistics, sys

DENTRO = "data/multichain/solana/gettoni.jsonl"
RITARDO, ORIZZONTE = 3, 750      # ~1 secondo, 5 minuti
FASCE = [("sotto il 10%", 0, .10), ("10-30%", .10, .30), ("30-50%", .30, .50), ("oltre il 50%", .50, 2)]


def conta(P):
    """ritorna (taratura, resa delle chiuse, resa con le bloccate a zero, quota bloccate)"""
    tara, chiuse, bloc, tot = [], [], 0, 0
    for i, (sl, p, compra, chi) in enumerate(P):
        if not compra:
            continue
        ing = next((j for j in range(i + 1, len(P)) if P[j][0] >= sl + RITARDO and P[j][2]), None)
        if ing is None or P[ing][1] <= 0:
            continue
        tot += 1
        sub = next((k for k in range(ing + 1, len(P)) if not P[k][2]), None)
        if sub is not None:
            tara.append(P[sub][1] / P[ing][1] - 1)
        usc = next((k for k in range(ing + 1, len(P))
                    if P[k][0] >= P[ing][0] + ORIZZONTE and not P[k][2]), None)
        if usc is None:
            bloc += 1
        else:
            chiuse.append(P[usc][1] / P[ing][1] - 1)
    if tot < 5 or not tara or not chiuse:
        return None
    tutte = chiuse + [-1.0] * bloc
    return (statistics.median(tara), statistics.median(chiuse), statistics.median(tutte), bloc / tot, tot)


def main():
    righe = []
    for r in open(DENTRO):
        d = json.loads(r)
        c = conta(sorted(d["s"]))
        if c:
            righe.append(c)
    print(f"LA RELAZIONE | {len(righe)} gettoni misurabili\n")
    print(f"   {'quota di posizioni bloccate':<28}{'gettoni':>9}{'taratura':>11}"
          f"{'resa SE chiuse':>17}{'resa con le bloccate a zero':>30}")
    print('   ' + '-' * 96)
    for et, a, b in FASCE:
        g = [x for x in righe if a <= x[3] < b]
        if len(g) < 3:
            print(f"   {et:<28}{len(g):>9}   (pochi)")
            continue
        print(f"   {et:<28}{len(g):>9}{statistics.median([x[0] for x in g])*100:>+10.2f}%"
              f"{statistics.median([x[1] for x in g])*100:>+16.2f}%"
              f"{statistics.median([x[2] for x in g])*100:>+29.2f}%")
    print('   ' + '-' * 96)
    # la correlazione, detta con un numero
    import math
    xs = [x[3] for x in righe]
    ys = [x[1] for x in righe]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    if den:
        print(f"\n   correlazione fra «quota bloccate» e «resa se chiuse»: {num/den:+.2f}")
        print("   (vicina a +1 = il guadagno apparente vive dove non si puo' uscire)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
