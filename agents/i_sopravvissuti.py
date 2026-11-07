"""I POCHI CHE SOPRAVVIVONO: la fetta che Nicolo' descriveva.

Su pump.fun nascono tantissimi gettoni, quasi tutti muoiono in pochi minuti — e quella fetta
l'abbiamo gia' misurata: comprarci dentro dopo il primo minuto e' una perdita quasi totale
perche' non si esce. Ma il mercato di cui si parla e' un altro: i POCHI che continuano a
vivere, e che poi possono esplodere.

Qui si separano le due popolazioni per DURATA DI VITA e si confrontano, con lo stesso metro:
taratura in cima, posizioni bloccate contate a zero, nessun filtro che usi il futuro... salvo
la durata stessa, che e' il criterio di separazione e viene DICHIARATA come tale.

ATTENZIONE, detto prima di leggere: «e' sopravvissuto» si sa dopo. Questa tabella NON e' una
strategia — e' una descrizione del mercato. Se la fetta lunga rende, il passo successivo e'
cercare un segno osservabile PRIMA che distingua i sopravvissuti.
"""
import json, os, statistics, sys

DENTRO = "data/multichain/solana/gettoni.jsonl"
RITARDO, ORIZZONTE = 3, 750
FASCE = [("muore in <5 min", 0, 5), ("5-30 min", 5, 30), ("30 min - 3 ore", 30, 180),
         ("oltre 3 ore", 180, 10 ** 9)]


def misura(P):
    tara, chiuse, bl, tot = [], [], 0, 0
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
            bl += 1
        else:
            chiuse.append(P[usc][1] / P[ing][1] - 1)
    if tot < 5 or not tara:
        return None
    return (statistics.median(tara), statistics.median(chiuse + [-1.0] * bl), bl / tot, tot)


def main():
    righe = []
    for r in open(DENTRO):
        d = json.loads(r)
        P = sorted(d["s"])
        if len(P) < 25:
            continue
        vita = (P[-1][0] - P[0][0]) * 0.4 / 60
        m = misura(P)
        if m:
            righe.append((vita, *m))
    print(f"I SOPRAVVISSUTI | {len(righe)} gettoni misurabili\n")
    print(f"   {'quanto vive il gettone':<22}{'gettoni':>9}{'quota':>8}{'bloccate':>11}"
          f"{'TARATURA':>11}{'resa':>10}{'differenza':>13}")
    print('   ' + '-' * 86)
    for et, a, b in FASCE:
        g = [x for x in righe if a <= x[0] < b]
        if len(g) < 3:
            print(f"   {et:<22}{len(g):>9}{len(g)/max(1,len(righe))*100:>7.0f}%   (pochi)")
            continue
        ta = statistics.median([x[1] for x in g])
        re = statistics.median([x[2] for x in g])
        print(f"   {et:<22}{len(g):>9}{len(g)/len(righe)*100:>7.0f}%"
              f"{statistics.median([x[3] for x in g])*100:>10.0f}%"
              f"{ta*100:>+10.2f}%{re*100:>+9.2f}%{(re-ta)*100:>+12.2f}")
    print('   ' + '-' * 86)
    print("   «quota» = che percentuale dei gettoni nati finisce in quella fascia.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
