"""SI PUO' SAPERE PRIMA SE SI RIUSCIRA' A USCIRE?

La relazione del 22/10 dice che il guadagno apparente e' l'invendibile, e che dove si esce la
resa e' piatta sul pedaggio. Ma «dove si esce» NON e' una cosa che sai quando compri: e' la
stessa trappola dei sopravvissuti che su Base aveva prodotto un +122% inesistente.

La domanda onesta: quello che si vede nei PRIMI SECONDI di vita di un gettone predice se poi
si riuscira' a uscire? Se si', esiste una regola di ammissione applicabile davvero.

Si misura cosi': per ogni gettone si guardano solo i primi 60 secondi (quanti scambi, quanti
compratori distinti, quanto grossi), e poi SEPARATAMENTE si guarda cosa e' successo dopo.
Nessun filtro che usi il futuro.
"""
import json, os, statistics, sys

DENTRO = "data/multichain/solana/gettoni.jsonl"
RITARDO, ORIZZONTE = 3, 750
PRIMI = 150        # 60 secondi: ~0,4s per slot


def main():
    righe = []
    for r in open(DENTRO):
        d = json.loads(r)
        P = sorted(d["s"])
        if len(P) < 30:
            continue
        s0 = P[0][0]
        primi = [x for x in P if x[0] - s0 <= PRIMI]
        if len(primi) < 5:
            continue
        # OSSERVABILE al secondo 60: niente di cio' che viene dopo
        oss = {"scambi": len(primi),
               "compratori": len({x[3] for x in primi if x[2]}),
               "quota_acquisti": sum(1 for x in primi if x[2]) / len(primi)}
        # ESITO: quante posizioni aperte DOPO il secondo 60 restano bloccate, e quanto rendono
        bl = tot = 0
        chiuse = []
        tara = []
        for i, (sl, p, compra, chi) in enumerate(P):
            if not compra or sl - s0 <= PRIMI:
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
            continue
        righe.append({**oss, "bloccate": bl / tot, "tot": tot,
                      "tara": statistics.median(tara),
                      "resa": statistics.median(chiuse + [-1.0] * bl)})
    print(f"SI POTRA' USCIRE | {len(righe)} gettoni con primi 60 secondi e seguito misurabili\n")
    if len(righe) < 8:
        print("   troppo pochi: serve altro accumulo")
        return 0
    for fam, fasce in (("scambi nei primi 60s", [("meno di 20", 0, 20), ("20-60", 20, 60), ("oltre 60", 60, 10**9)]),
                       ("compratori distinti", [("meno di 10", 0, 10), ("10-30", 10, 30), ("oltre 30", 30, 10**9)])):
        print(f"   {fam:<26}{'gettoni':>9}{'bloccate poi':>14}{'TARATURA':>11}{'resa':>10}{'differenza':>13}")
        print('   ' + '-' * 84)
        ch = "scambi" if fam.startswith("scambi") else "compratori"
        for et, a, b in fasce:
            g = [x for x in righe if a <= x[ch] < b]
            if len(g) < 3:
                print(f"   {et:<26}{len(g):>9}   (pochi)")
                continue
            ta = statistics.median([x["tara"] for x in g])
            re = statistics.median([x["resa"] for x in g])
            print(f"   {et:<26}{len(g):>9}{statistics.median([x['bloccate'] for x in g])*100:>13.0f}%"
                  f"{ta*100:>+10.2f}%{re*100:>+9.2f}%{(re-ta)*100:>+12.2f}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
