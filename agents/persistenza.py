"""Chi era bravo prima e' bravo anche dopo? Il test fuori campione nel tempo.

PERCHE' E' QUESTO IL TEST (5/10). Finora ogni misura sui vincenti era circolare: li scegliavo
perche' avevano fatto multipli alti, e poi constatavo che avevano fatto multipli alti. Il
gruppo di controllo ha risolto meta' del problema (il portafoglio tipico sta a 1,06-1,13X,
quindi i multipli ripetuti NON sono come funziona il mercato) ma non l'altra meta': la
selezione usava le STESSE posizioni della misura.

QUI NO. Si ordinano le posizioni chiuse di ogni portafoglio nel tempo, si guarda SOLO la prima
meta' per decidere se era bravo, e si misura SOLO la seconda. I due insiemi sono disgiunti per
costruzione, e la soglia («bravo» = mediana >=2X sulla prima meta') e' scritta prima.

PERCHE' L'EFFETTO DI DISPOSIZIONE NON LO SPIEGA. Entrambi i gruppi sono misurati sulle sole
posizioni chiuse, cioe' su quelle che hanno scelto di vendere. Quel difetto gonfia il LIVELLO
di tutti e due, non il DIVARIO fra loro — ed e' il divario che si legge qui. E' lo stesso
ragionamento con cui il 4/10 il 93% di vincenti e' caduto: la' il confronto non c'era, qui si'.

E PERCHE' LA SOPRAVVIVENZA NON LO SPIEGA. Per entrare serve >=6 posizioni chiuse, lo stesso
requisito per entrambi i gruppi: «essere ancora qui» e' tenuto fermo per costruzione.
"""
import glob
import json
import os
import sys

import numpy as np

SOGLIA = 2.0        # «bravo prima» = mediana almeno 2X sulla prima meta'
MIN_CHIUSE = 6      # almeno tre prima e tre dopo


def carica(chain, cartella):
    det = {}
    for p in glob.glob(f"{cartella}/*/multichain/{chain}/dettaglio_candidati_pezzo_*.json"):
        for k, v in json.load(open(p)).items():
            det.setdefault(k, {}).update(v)
    if not det:
        p = f"data/multichain/{chain}/dettaglio_candidati.json.gz"
        if os.path.exists(p):
            import gzip
            raw = json.load(gzip.open(p, "rt"))
            det = raw.get("da", raw)
    return det


def main():
    cartella = sys.argv[1] if len(sys.argv) > 1 else "/tmp/art"
    for chain in ("base", "robinhood"):
        det = carica(chain, cartella)
        bravi, scarsi = [], []
        for pools in det.values():
            z = [(v.get("primo"), v["multiplo"]) for v in pools.values()
                 if v.get("stato") == "chiuso" and v.get("multiplo")
                 and not v.get("sospetto") and v.get("primo")]
            if len(z) < MIN_CHIUSE:
                continue
            z.sort()
            h = len(z) // 2
            prima = np.array([m for _, m in z[:h]])
            dopo = np.array([m for _, m in z[h:]])
            (bravi if np.median(prima) >= SOGLIA else scarsi).append(
                (float(np.median(prima)), float(np.median(dopo)), float(np.mean(dopo >= 2))))
        print(f"\n=== {chain}: {len(bravi)+len(scarsi)} portafogli con almeno "
              f"{MIN_CHIUSE} posizioni chiuse ===")
        print(f"   {'giudicati sul PASSATO':<26} {'n':>4} {'mediana PRIMA':>14} "
              f"{'mediana DOPO':>13} {'>=2X dopo':>11}")
        for nome, g in (("bravi prima (>=2X)", bravi), ("scarsi prima (<2X)", scarsi)):
            if len(g) < 5:
                print(f"   {nome:<26} {len(g):>4}  troppo pochi per giudicare")
                continue
            pr = np.array([x[0] for x in g])
            dp = np.array([x[1] for x in g])
            q = np.array([x[2] for x in g])
            print(f"   {nome:<26} {len(g):>4} {np.median(pr):13.2f}X "
                  f"{np.median(dp):12.2f}X {np.median(q):10.0%}")
        if len(bravi) >= 5 and len(scarsi) >= 5:
            a = float(np.median([x[1] for x in bravi]))
            b = float(np.median([x[1] for x in scarsi]))
            print(f"   divario sul FUTURO: {a:.2f}X contro {b:.2f}X — "
                  f"{'i bravi restano bravi' if a > b else 'NESSUNA persistenza'}")


if __name__ == "__main__":
    main()
