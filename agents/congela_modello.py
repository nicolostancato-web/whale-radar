"""Congela il modello di selezione COSI' COM'E' OGGI, per poterlo giudicare sul futuro.

PERCHE' ESISTE (30/09). La selezione e' stata bocciata quindici volte — ma sul dato corretto
batte il fondale in undici finestre su dodici, di +24,6 punti. E' il secondo candidato, accanto
al «compra tutto piccolo e presto» gia' registrato in PROVA_IN_AVANTI.md.

Un modello che si riaddestra ogni giorno NON si puo' giudicare sul futuro: quando arriva il
verdetto, ha gia' visto i dati su cui lo giudichi. Quindi si congela adesso — pesi scritti su
disco, con la data e il numero di pool su cui ha imparato — e da qui in poi si applica e basta.

Se il modello congelato batte il fondale sui pool nati DOPO oggi, e' un vantaggio vero.
Se lo batte solo quando si riaddestra, era memoria del passato.
"""
import gzip
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modello import addestra                                    # noqa: E402

FUORI = "data/loop1/modello_congelato.json"


def main():
    pesi = {}
    for chain in ("robinhood", "base"):
        p = f"data/loop1/insieme_{chain}_sc5.jsonl.gz"
        if not os.path.exists(p):
            print(f"CONGELO | {chain}: manca {p}", flush=True)
            continue
        r = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
        r = [x for x in r if x.get("_giudicabile") and x.get("_uscita_25") is not None]
        if len(r) < 2000:
            print(f"CONGELO | {chain}: solo {len(r)} pool, non congelo", flush=True)
            continue
        r.sort(key=lambda x: x["_t"])
        nomi = sorted(k for k in r[0] if not k.startswith("_"))
        X = np.clip(np.nan_to_num(np.array([[float(x[k]) for k in nomi] for x in r], dtype=float),
                                  nan=0.0, posinf=0.0, neginf=0.0), -1e12, 1e12)
        y = np.array([1.0 if x["_uscita_25"] >= 0.0 else 0.0 for x in r])
        mu, sd = X.mean(0), X.std(0) + 1e-9
        w, b = addestra((X - mu) / sd, y, penalita=1.0, giri=3000)
        pesi[chain] = {"nomi": nomi, "w": [float(v) for v in w], "b": float(b),
                       "mu": [float(v) for v in mu], "sd": [float(v) for v in sd],
                       "pool_di_addestramento": len(r),
                       "ultimo_pool_nato": int(r[-1]["_t"])}
        print(f"CONGELO | {chain}: {len(r)} pool, {len(nomi)} caratteristiche", flush=True)
    if pesi:
        os.makedirs(os.path.dirname(FUORI), exist_ok=True)
        json.dump(pesi, open(FUORI, "w"), indent=1, sort_keys=True)
        print(f"CONGELO | scritto {FUORI} — da qui in poi si applica, non si riaddestra",
              flush=True)


if __name__ == "__main__":
    main()
