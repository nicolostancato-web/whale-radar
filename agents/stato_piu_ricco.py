"""Fra due copie dello stesso stato, tiene quella con piu' posizioni.

VINCE IL PIU' RICCO, NON IL PIU' RECENTE (13/10). Al primo giro della corsia l'allegato non
esisteva e la prova e' ripartita da zero, mentre sul ramo c'erano 705 posizioni gia'
accumulate: prendere sempre l'allegato avrebbe buttato via tutto il passato ogni volta che la
corsia riparte pulita. Un ripristino che puo' perdere dati non e' un ripristino.
"""
import json
import shutil
import sys


def quante(percorso):
    try:
        with open(percorso) as f:
            return len(json.load(f).get("posizioni") or {})
    except Exception:
        return -1


def main():
    allegato, ramo = sys.argv[1], sys.argv[2]
    a, r = quante(allegato), quante(ramo)
    print(f"allegato: {a} posizioni, ramo: {r} posizioni")
    if a >= r:
        shutil.copy(allegato, ramo)
        print("tengo l'allegato")
    else:
        print("tengo il ramo: l'allegato e' piu' povero")
    return 0


if __name__ == "__main__":
    sys.exit(main())
