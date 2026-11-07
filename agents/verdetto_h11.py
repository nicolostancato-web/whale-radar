"""H10 — la successione di pattern di H9, ma tenendo 168 ore invece di 6.

Le regole sono state scritte in IPOTESI_H10.md PRIMA di guardare questo risultato:
divisione nel TEMPO (70/30), giudizio solo sulla vendita simulata da $500, media TAGLIATA
(via il 5% migliore e il 5% peggiore), e serve su TUTTE E DUE le chain.

Fra −5% e 0% NON e' un successo: e' un «quasi» che non si spaccia per vittoria.
"""
import gzip
import json
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from modello import addestra, prevedi                      # noqa: E402

SUFFISSO = "_h168"
MINIMO = 400            # sotto questo numero di pool nel campione di prova non si giudica


def taglia(v):
    """Media tagliata: via il 5% migliore e il 5% peggiore. Un colpo solo non e' una strategia."""
    v = np.sort(np.asarray(v))
    k = max(1, int(len(v) * 0.05))
    return float(v[k:len(v) - k].mean())


def una_chain(chain, suffisso):
    p = f"data/loop1/insieme_{chain}{suffisso}.jsonl.gz"
    r = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
    r = [x for x in r if x.get("_giudicabile") and x.get("_uscita_500") is not None]
    if len(r) < MINIMO * 3:
        return None
    r.sort(key=lambda x: x["_t"])
    nomi = sorted(k for k in r[0] if not k.startswith("_"))
    X = np.clip(np.nan_to_num(np.array([[float(x[k]) for k in nomi] for x in r], dtype=float),
                              nan=0.0, posinf=0.0, neginf=0.0), -1e12, 1e12)
    # H11 (29/09): SI IMPARA SU QUELLO CHE SI INCASSA, NON SU QUANTO SALE.
    # Con il bersaglio «fara' +50% di prezzo» il modello sceglieva i pool piu' sottili — quelli
    # che schizzano proprio perche' non c'e' nessuno dentro — e su robinhood il suo decimo
    # migliore incassava −69% contro un fondale di −27%: peggio del caso. Il bersaglio giusto
    # e' l'unico che conta: chi vende $500 veri ci esce in pari?
    BERSAGLIO_INCASSO = float(__import__("os").environ.get("SOGLIA", 0.0))
    y = np.array([1.0 if x["_uscita_500"] >= BERSAGLIO_INCASSO else 0.0 for x in r])
    inc = np.array([x["_uscita_500"] for x in r])           # cio' che si incassa davvero

    # LA DIVISIONE E' NEL TEMPO. A caso si imparerebbe dal futuro: i pool nati vicini si
    # somigliano, e mezzo pool nel passato basta a spiegare l'altro mezzo nel futuro.
    t = int(len(r) * 0.7)
    mu, sd = X[:t].mean(0), X[:t].std(0) + 1e-9
    w, b = addestra((X[:t] - mu) / sd, y[:t], penalita=1.0, giri=3000)
    s = prevedi((X[t:] - mu) / sd, w, b)
    fuori = inc[t:]
    if len(fuori) < MINIMO:
        return None

    ordine = np.argsort(-s)
    decile = ordine[:max(20, len(ordine) // 10)]
    return {"pool_di_prova": len(fuori),
            "fondale": 100 * taglia(fuori),
            "decile": 100 * taglia(fuori[decile]),
            "quinti": [round(100 * taglia(fuori[ordine[i * len(ordine) // 5:
                                                       (i + 1) * len(ordine) // 5]]), 1)
                       for i in range(5)]}


def main():
    print("H11 | si impara su quello che si INCASSA, non su quanto sale", flush=True)
    esiti = {}
    for chain in ("robinhood", "base"):
        e = una_chain(chain, SUFFISSO)
        base_6h = una_chain(chain, "")
        if not e:
            print(f"   {chain}: troppo pochi pool per giudicare", flush=True)
            return
        esiti[chain] = e
        print(f"\n   --- {chain}: {e['pool_di_prova']} pool mai visti ---", flush=True)
        print(f"   fondale (tutti)          {e['fondale']:+7.1f}%", flush=True)
        print(f"   decimo migliore          {e['decile']:+7.1f}%   "
              f"({e['decile'] - e['fondale']:+.1f} punti sopra il fondale)", flush=True)
        print(f"   dal preferito allo scartato  {e['quinti']}", flush=True)
        if base_6h:
            print(f"   [a 6 ore lo stesso decile valeva {base_6h['decile']:+.1f}%]", flush=True)

    print("\n" + "=" * 62, flush=True)
    sopra = [c for c, e in esiti.items() if e["decile"] > 0]
    quasi = [c for c, e in esiti.items() if -5 <= e["decile"] <= 0]
    if len(sopra) == 2:
        print("   SOPRAVVIVE: il decimo migliore sta sopra zero su tutte e due.", flush=True)
        print("   Non e' ancora una strategia: e' la prima che non muore.", flush=True)
    elif sopra:
        print(f"   MUORE: sta sopra zero solo su {sopra[0]}. Una sola chain e' rumore,", flush=True)
        print("   e questa regola era scritta prima di guardare.", flush=True)
    elif quasi:
        print(f"   MUORE, ma da vicino: {', '.join(quasi)} fra −5% e 0%.", flush=True)
        print("   Un «quasi» non si spaccia per vittoria: era scritto nell'ipotesi.", flush=True)
    else:
        print("   MUORE. La finestra vale punti, ma non abbastanza da pagare.", flush=True)


if __name__ == "__main__":
    main()
