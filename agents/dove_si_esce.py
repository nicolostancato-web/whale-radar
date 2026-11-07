"""DENTRO LA FETTA DOVE SI ESCE: esiste una condizione che batte il pedaggio?

La relazione del 22/10 dice che il guadagno apparente E' l'invendibile. Resta una domanda
precisa e utile: nella fetta dove si esce quasi sempre (meno del 10% di bloccate), e dove
quindi i numeri sono veri, c'e' qualche condizione OSSERVABILE PRIMA di comprare che porti la
resa sopra il pedaggio?

Tre condizioni, tutte leggibili al momento dell'acquisto:
  - quanti scambi ha avuto il gettone nei 60 secondi precedenti
  - quanto e' grosso l'acquisto che stiamo seguendo
  - da quanto tempo quel gettone scambia (eta' nella nostra serie)

Niente di nuovo come metodo: taratura in cima a ogni fascia, bloccate contate, e si legge solo
dove la taratura e' negativa.
"""
import bisect, collections, json, os, statistics, sys

DENTRO = "data/multichain/solana/gettoni.jsonl"
RITARDO, ORIZZONTE, PRIMA = 3, 750, 150     # 1s, 5 min, 1 min di storia osservabile


def main():
    agg = collections.defaultdict(lambda: {"tara": [], "chiuse": [], "bloc": 0, "tot": 0})
    usati = scartati = 0
    for r in open(DENTRO):
        d = json.loads(r)
        P = sorted(d["s"])
        if len(P) < 40:
            continue
        # prima si calcola la quota di bloccate del gettone: si tiene solo chi esce quasi sempre
        bl = sl = 0
        for i, (s_, p, c_, chi) in enumerate(P):
            if not c_:
                continue
            ing = next((j for j in range(i + 1, len(P)) if P[j][0] >= s_ + RITARDO and P[j][2]), None)
            if ing is None:
                continue
            sl += 1
            if not any(P[k][0] >= P[ing][0] + ORIZZONTE and not P[k][2] for k in range(ing + 1, len(P))):
                bl += 1
        if sl < 5 or bl / sl > 0.10:
            scartati += 1
            continue
        usati += 1
        slots = [x[0] for x in P]
        for i, (s_, p, compra, chi) in enumerate(P):
            if not compra:
                continue
            ing = next((j for j in range(i + 1, len(P)) if P[j][0] >= s_ + RITARDO and P[j][2]), None)
            if ing is None or P[ing][1] <= 0:
                continue
            att = i - bisect.bisect_left(slots, s_ - PRIMA)
            eta = (s_ - P[0][0]) * 0.4
            chiavi = [("attivita", "poca" if att < 5 else ("media" if att < 20 else "molta")),
                      ("eta", "primi 5 min" if eta < 300 else ("5-30 min" if eta < 1800 else "oltre"))]
            sub = next((k for k in range(ing + 1, len(P)) if not P[k][2]), None)
            usc = next((k for k in range(ing + 1, len(P))
                        if P[k][0] >= P[ing][0] + ORIZZONTE and not P[k][2]), None)
            for fam, val in chiavi:
                g = agg[(fam, val)]
                g["tot"] += 1
                if sub is not None:
                    g["tara"].append(P[sub][1] / P[ing][1] - 1)
                if usc is None:
                    g["bloc"] += 1
                else:
                    g["chiuse"].append(P[usc][1] / P[ing][1] - 1)
    print(f"DOVE SI ESCE | {usati} gettoni con meno del 10% di bloccate "
          f"({scartati} scartati perche' non si esce)\n")
    print(f"   {'condizione':<28}{'operazioni':>12}{'TARATURA':>11}{'resa a 5 min':>15}{'differenza':>13}")
    print('   ' + '-' * 82)
    for k in sorted(agg):
        g = agg[k]
        if g["tot"] < 40 or not g["tara"] or not g["chiuse"]:
            continue
        ta = statistics.median(g["tara"])
        re = statistics.median(g["chiuse"] + [-1.0] * g["bloc"])
        print(f"   {k[0]+': '+k[1]:<28}{g['tot']:>12,}{ta*100:>+10.2f}%{re*100:>+14.2f}%{(re-ta)*100:>+12.2f}")
    print('   ' + '-' * 82)
    print("   si legge solo dove la TARATURA e' negativa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
