"""CHI GUADAGNA DAVVERO SU PUMP.FUN — e se vale copiarlo.

Su Solana ogni riga del nostro archivio porta gia' CHI ha fatto l'operazione: identita' e
prezzo arrivano nella stessa lettura. Su Robinhood era stata una notte separata e 41 milioni
di righe; su Base e' il muro contro cui ci siamo fermati.

Due misure diverse, e vanno tenute separate perche' rispondono a domande diverse:
  A) QUANTO HA GUADAGNATO LUI — profitto realizzato sul suo prezzo. Dice chi e' bravo.
  B) QUANTO RENDEREBBE A NOI COPIARLO — entrata un secondo dopo la sua, uscita su una vendita.
     Dice se e' copiabile. Sono due cose diverse: su Robinhood la (A) era ottima e la (B)
     negativa per gli stessi portafogli.

E le protezioni di sempre: posizioni mai chiuse contate e non scartate, taratura di
riferimento, e i portafogli raggruppati in ENTITA' prima di contarli — perche' due volte su
due i «migliori» erano un operatore solo con quattro indirizzi.
"""
import collections, json, os, statistics, sys

DENTRO = "data/multichain/solana/gettoni.jsonl"
RITARDO, ORIZZONTE = 3, 750


def main():
    # A) profitto realizzato di ogni portafoglio: quanto SOL dentro, quanto fuori
    speso = collections.Counter()
    incassato = collections.Counter()
    gettoni_di = collections.defaultdict(set)
    slot_di = collections.defaultdict(set)
    # B) cosa renderebbe seguirlo
    copia = collections.defaultdict(list)
    rif = []
    for r in open(DENTRO):
        d = json.loads(r)
        P = sorted(d["s"])
        if len(P) < 25:
            continue
        for i, (sl, p, compra, chi) in enumerate(P):
            gettoni_di[chi].add(d["g"])
            slot_di[chi].add(sl)
            if compra:
                speso[chi] += p
            else:
                incassato[chi] += p
            if not compra:
                continue
            ing = next((j for j in range(i + 1, len(P)) if P[j][0] >= sl + RITARDO and P[j][2]), None)
            if ing is None or P[ing][1] <= 0:
                continue
            usc = next((k for k in range(ing + 1, len(P))
                        if P[k][0] >= P[ing][0] + ORIZZONTE and not P[k][2]), None)
            e = (P[usc][1] / P[ing][1] - 1) if usc is not None else -1.0
            copia[chi].append(e)
            rif.append(e)
    print(f"PORTAFOGLI SOL | {len(gettoni_di):,} indirizzi, {len(rif):,} operazioni seguibili\n")
    attivi = [w for w in gettoni_di if len(gettoni_di[w]) >= 3 and len(copia.get(w, [])) >= 5]
    print(f"   indirizzi con almeno 3 gettoni e 5 operazioni seguibili: {len(attivi)}")
    if rif:
        print(f"   RIFERIMENTO, seguire un acquisto qualunque: {statistics.median(rif)*100:+.2f}% "
              f"su {len(rif):,} operazioni")
    if not attivi:
        print("   troppo pochi: serve altro accumulo")
        return 0
    # entita': stesso operatore se condividono molti slot E molti gettoni
    padre = {w: w for w in attivi}
    def trova(x):
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x
    fuse = 0
    for a in range(len(attivi)):
        for b in range(a + 1, len(attivi)):
            x, y = attivi[a], attivi[b]
            gs = gettoni_di[x] & gettoni_di[y]
            sl = slot_di[x] & slot_di[y]
            if len(gs) >= 3 and len(sl) >= 5:
                rx, ry = trova(x), trova(y)
                if rx != ry:
                    padre[rx] = ry
                    fuse += 1
    ent = collections.defaultdict(list)
    for w in attivi:
        ent[trova(w)].extend(copia[w])
    print(f"   fusioni fra indirizzi dello stesso operatore: {fuse}  ->  entita' {len(ent)}\n")
    # A) chi guadagna: profitto realizzato
    prof = []
    for w in attivi:
        s, i = speso[w], incassato[w]
        if s > 0:
            prof.append((i / s - 1, w))
    prof.sort(reverse=True)
    print(f"   A) PROFITTO REALIZZATO (incassato/speso): mediana {statistics.median([x for x,_ in prof])*100:+.1f}%, "
          f"in utile {sum(1 for x,_ in prof if x>0)/len(prof)*100:.0f}%")
    print(f"      i migliori: " + ", ".join(f"{w[:8]} {x*100:+.0f}%" for x, w in prof[:4]))
    # B) copiabilita' per entita'
    m = [(statistics.median(v), len(v), k) for k, v in ent.items() if len(v) >= 5]
    m.sort(reverse=True)
    print(f"\n   B) SE LI COPIASSIMO, per entita' ({len(m)} entita'):")
    print(f"      mediana fra le entita': {statistics.median([x for x,_,_ in m])*100:+.2f}%")
    print(f"      quante battono il riferimento: {sum(1 for x,_,_ in m if x>statistics.median(rif))}/{len(m)}")
    print(f"      le migliori: " + ", ".join(f"{k[:8]} {x*100:+.0f}% su {n}" for x, n, k in m[:4]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
