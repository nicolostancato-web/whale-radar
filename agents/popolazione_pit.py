"""POPOLAZIONE POINT-IN-TIME — chi studiamo, deciso con cio' che si sapeva allora.

Quinto pezzo del loop 1, ed e' quello che sblocca gli altri: finche' la popolazione guarda il
futuro, ogni risultato calcolato su di essa e' contaminato, per quanto sia pulito il resto.

IL DIFETTO CHE CORREGGE. La regola attuale dice: «un pool entra se ha almeno 20 scambi
nell'intervallo dichiarato». Ma quell'intervallo dura settimane. Quindi un pool entra nella
popolazione GRAZIE A QUELLO CHE HA FATTO DOPO il momento in cui avremmo dovuto decidere.
Trovato indipendentemente da Codex e da Astra, a poche ore di distanza — quando due revisori
diversi inciampano nella stessa cosa, non e' una sfumatura.

Conseguenza concreta: un pool che al momento della decisione aveva due scambi, e nei giorni
successivi e' arrivato a venti, oggi fa parte dello studio. Uno che ne aveva diciannove ed e' morto
la' e' escluso. Studiare quel gruppo e chiamarlo «il mercato» significa studiare i sopravvissuti.

LA REGOLA NUOVA. Un pool entra se ha fatto almeno N scambi entro X ore dal PRIMO momento in cui
l'abbiamo visto. Tutto cio' che serve per decidere e' disponibile a quell'ora: niente di piu'.

COSA MISURA QUESTO AGENTE. Non impone la regola: misura QUANTO CAMBIA la popolazione al variare di
N e X, e quanto pesa la contaminazione della regola vecchia. La soglia si sceglie dopo aver visto
i numeri, e si dichiara prima di usarla — non il contrario.

IL LIMITE, GIA' NOTO E DICHIARATO: per il 74% dei pool su base e il 91% su robinhood il «primo
momento in cui l'abbiamo visto» NON e' la nascita del pool: siamo arrivati dopo (misurato il
22/09). Quindi la finestra di X ore parte da quando siamo arrivati noi, non da quando e' nato lui.
Per i pool di cui abbiamo la nascita vera la finestra parte da li', ed e' segnalato nel risultato.
"""
import gzip
import json
import os
from collections import defaultdict

CHAIN = os.environ.get("CHAIN", "base")
FUORI = f"data/loop1/popolazione_pit_{CHAIN}.json"
ORE = [1, 3, 6, 24]
SOGLIE = [5, 10, 20]


def nascite_vere():
    f = f"data/multichain/{CHAIN}/nascita_vera.json"
    try:
        d = json.load(open(f)).get("nascite", {})
    except Exception:
        return {}
    return {k.lower(): v["ts"] for k, v in d.items()
            if v.get("fonte") == "catena" and v.get("ts")}


def main():
    nasc = nascite_vere()
    per_pool = defaultdict(list)
    for sub in ("storico", "vivo"):
        d = f"data/multichain/{CHAIN}/{sub}"
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            try:
                righe = [json.loads(l) for l in gzip.open(os.path.join(d, fn), "rt") if l.strip()]
            except Exception:
                continue
            per_pool[fn.split(".")[0].lower()].extend(righe)

    conta = {(o, s): 0 for o in ORE for s in SOGLIE}
    con_nascita = {(o, s): 0 for o in ORE for s in SOGLIE}
    vecchia = 0
    totale = 0
    contaminati = {(o, s): 0 for o in ORE for s in SOGLIE}

    for pool, righe in per_pool.items():
        ts = sorted(r["ts"] for r in righe if r.get("ts"))
        if not ts:
            continue
        totale += 1
        # la regola VECCHIA: venti scambi in tutto l'intervallo, quando che sia
        dentro_vecchia = len(ts) >= 20
        if dentro_vecchia:
            vecchia += 1
        # il momento da cui si conta: la nascita se ce l'abbiamo, altrimenti il primo che vediamo
        t0 = nasc.get(pool, ts[0])
        ho_nascita = pool in nasc
        for o in ORE:
            limite = t0 + o * 3600
            quanti = sum(1 for t in ts if t <= limite)
            for s in SOGLIE:
                if quanti >= s:
                    conta[(o, s)] += 1
                    if ho_nascita:
                        con_nascita[(o, s)] += 1
                # CONTAMINATO = entrava con la regola vecchia ma NON con quella onesta.
                # E' la misura di quanto la popolazione attuale e' fatta di sopravvissuti.
                elif dentro_vecchia:
                    contaminati[(o, s)] += 1

    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    json.dump({"totale": totale, "regola_vecchia": vecchia,
               "pit": {f"{o}h_{s}": conta[(o, s)] for o in ORE for s in SOGLIE},
               "con_nascita_vera": {f"{o}h_{s}": con_nascita[(o, s)] for o in ORE for s in SOGLIE},
               "contaminati": {f"{o}h_{s}": contaminati[(o, s)] for o in ORE for s in SOGLIE}},
              open(FUORI, "w"), indent=1)

    print(f"POPOLAZIONE | {CHAIN}: {totale} pool con almeno uno scambio")
    print(f"   regola VECCHIA (>=20 scambi quando che sia): {vecchia} pool "
          f"= {100*vecchia/max(1,totale):.1f}%")
    print()
    print(f"   regola ONESTA (N scambi entro X ore dal primo momento noto):")
    print(f"      {'':>6} " + "  ".join(f"{s:>7} scambi" for s in SOGLIE))
    for o in ORE:
        riga = f"      {o:>3}h  "
        for s in SOGLIE:
            riga += f"{conta[(o,s)]:>8} ({100*conta[(o,s)]/max(1,totale):>4.1f}%)"
        print(riga)
    print()
    print(f"   CONTAMINATI — entravano con la vecchia regola grazie a cio' che hanno fatto DOPO:")
    for o in ORE:
        riga = f"      {o:>3}h  "
        for s in SOGLIE:
            c = contaminati[(o, s)]
            riga += f"{c:>8} ({100*c/max(1,vecchia):>4.1f}% della vecchia)"
        print(riga)
    print()
    print(f"   pool di cui abbiamo la NASCITA vera: {len(nasc)}")
    print(f"      per gli altri la finestra parte da quando siamo arrivati NOI, non dalla nascita.")
    print(f"   scritto {FUORI}")


if __name__ == "__main__":
    main()
