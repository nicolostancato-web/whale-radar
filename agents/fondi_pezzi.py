"""Fonde i pezzi di una raccolta a fette in un archivio unico. Si lancia dove di scrittori ce n'e' uno.

PERCHE' E' GENERICO (2/10). Ho scritto tre volte lo stesso meccanismo di fusione — per gli
iniziatori, per i nonce, per i finanziatori — e la terza volta l'ho sbagliata. Un meccanismo
scritto tre volte diverge tre volte: qui ce n'e' uno, e chi aggiunge una raccolta a fette lo usa.

uso:  python agents/fondi_pezzi.py <chain> <nome>
  legge  data/multichain/<chain>/<nome>_pezzo_*.json
  scrive data/multichain/<chain>/<nome>.json.gz   (fondendo con quello che c'e' gia')
  cancella TUTTI i pezzi fusi, non uno.
"""
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a_fette as AF                                              # noqa: E402


def main():
    if len(sys.argv) < 3:
        raise SystemExit("uso: fondi_pezzi.py <chain> <nome>")
    chain, nome = sys.argv[1], sys.argv[2]
    radice = f"data/multichain/{chain}"
    pezzi = AF.pezzi(radice, nome)
    if not pezzi:
        print(f"PEZZI | {chain}/{nome}: nessun pezzo")
        return 0
    nuovi = {}
    rotti = 0
    for q in pezzi:
        try:
            nuovi.update(json.load(open(q)))
        except Exception:
            rotti += 1
    if not nuovi:
        print(f"PEZZI | {chain}/{nome}: {len(pezzi)} pezzi, tutti vuoti o illeggibili "
              f"({rotti}): NON tocco l'archivio")
        return 1
    f = os.path.join(radice, f"{nome}.json.gz")
    vecchi = {}
    if os.path.exists(f):
        try:
            vecchi = json.load(gzip.open(f, "rt")).get("da", {})
        except Exception:
            vecchi = {}
    prima = len(vecchi)
    vecchi.update(nuovi)
    with gzip.open(f, "wt") as h:
        json.dump({"acq": int(time.time()), "da": vecchi}, h)
    for q in pezzi:
        try:
            os.remove(q)
        except Exception:
            pass
    import collections
    gruppi = collections.Counter(vecchi.values())
    flotte = [(k, v) for k, v in gruppi.items() if v >= 3]
    print(f"PEZZI | {chain}/{nome}: {len(pezzi)} pezzi, {prima:,} -> {len(vecchi):,} "
          f"({len(gruppi):,} valori distinti, {len(flotte):,} con 3+)")
    for k, v in sorted(flotte, key=lambda kv: -kv[1])[:5]:
        print(f"   flotta: {k[:16]}… ne raggruppa {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
